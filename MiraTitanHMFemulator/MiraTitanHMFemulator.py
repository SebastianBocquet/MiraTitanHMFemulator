import numpy as np
import os
import inspect

from scipy.interpolate import RectBivariateSpline

from . import GP_matrix as GP


class Emulator:
    """The Mira-Titan Universe emulator for the halo mass function.

    Attributes
    -----------------
    param_limits : dictionary
        Lower and upper limits of the cosmological parameters.
    z_arr : array
        Redshifts of the emulator output.
    """
    # Cosmology parameters
    # __param_names = ('Ommh2', 'Ombh2', 'Omnuh2', 'n_s', 'h', 'sigma_8', 'w_0', 'w_b')
    param_limits = {
        'Ommh2': (.12, .155),
        'Ombh2': (.0215, .0235),
        'Omnuh2': (0, .01),
        'n_s': (.85, 1.05),
        'h': (.55, .85),
        'sigma_8': (.7, .9),
        'w_0': (-1.3, -.7),
        'w_b': (.3, 1.3),
    }
    # Emulator redshifts
    z_arr = np.array([2.02, 1.61, 1.01, 0.656, 0.434, 0.242, 0.101, 0.0])
    z_arr_asc = z_arr[::-1]



    def __init__(self):
        """No arguments are required when initializing an `Emulator` instance.
        Upon initialization, a bunch of matrix operations are performed which
        takes a few seconds."""
        data_path = os.path.join(os.path.dirname(os.path.abspath(inspect.stack()[0][1])), 'data')

        # Basis functions and PCA standardization parameters
        # They have different lengths so they are stored in separate files
        self.__PCA_means, self.__PCA_transform = [], []
        for i in range(len(self.z_arr)):
            filename = os.path.join(data_path, 'PCA_mean_std_transform_%d.npy'%i)
            _tmp = np.load(filename)
            self.__PCA_means.append(_tmp[0,:])
            self.__PCA_transform.append(_tmp[1:,:])
        self.__GP_means = np.load(os.path.join(data_path, 'GP_params_mean.npy'))
        self.__GP_std = np.load(os.path.join(data_path, 'GP_params_std.npy'))
        self.__facs = np.load(os.path.join(data_path, 'facs.npy'))

        # GP input data
        params_design = np.load(os.path.join(data_path, 'params_design_w0wb.npy'))
        hyper_params = np.load(os.path.join(data_path, 'hyperparams.npy'))
        input_means = np.load(os.path.join(data_path, 'means.npy'))
        cov_mat_data = np.load(os.path.join(data_path, 'cov_n.npy'))
        N_PC = input_means.shape[2]
        self.__GPreg = [GP.GaussianProcess(params_design,
                                           input_means[z_id],
                                           cov_mat_data[z_id],
                                           hyper_params[z_id,:N_PC],
                                           hyper_params[z_id,N_PC:].reshape(N_PC,-1))
                        for z_id in range(len(self.z_arr))]


    def predict(self, requested_cosmology, z, m, get_errors=True, N_draw=1000):
        """Emulate the halo mass function dn/dlnM for the desired set of
        cosmology parameters, redshifts, and masses.

        :param requested_cosmology: The set of cosmology parameters for which
            the mass function is requested. The parameters are `Ommh2`, `Ombh2`,
            `Omnuh2`, `n_s`, `h`, `sigma_8`, `w_0`, `w_a`.
        :type requested_cosmology: dict

        :param z: The redshift(s) for which the mass function is requested.
        :type z: float or array

        :param m: The mass(es) for which the mass function is requested, in
            units [Msun/h].
        :type z: float or array

        :param get_errors: Whether or not to compute error estimates (faster in
            the latter case). Default is `True`.
        :type get_errors:  bool, optional

        :param N_draw: How many sample mass functions to draw when computing the
            error estimate. Applies only if `get_errors` is `True`.
        :type N_draw: int, optional

        Returns
        -------
        HMF: array_like
            The mass function dN/dlnM in units[(h/Mpc)^3] and with shape
            [len(z), len(m)].
        HMF_rel_err: array_like
            The relative error on dN/dlnM, with shape [len(z), len(m)]. Returns 0
            if `get_errors` is `False`. For requested redshifts that are between
            the redshifts for which the underlying emulator is defined, the
            weighted errors from the neighboring redshifts are added in
            quadrature.
        """
        # Validate requested z and m
        if np.any(z<0):
            raise ValueError("z must be >= 0")
        if np.any(z>self.z_arr_asc[-1]):
            raise ValueError("z must be <= 2.02")
        if np.any(m<1e13):
            raise ValueError("m must be >= 1e13")
        if np.any(m>1e16):
            raise ValueError("m must be <= 1e16")
        z = np.atleast_1d(z)
        m = np.atleast_1d(m)

        # Do we want error estimates?
        if not get_errors:
            N_draw = 0

        # Call the actual emulator
        emu_dict = self.predict_raw_emu(requested_cosmology, N_draw=N_draw)

        # Set up interpolation grids
        HMF_interp_input = np.log(np.nextafter(0,1)) * np.ones((len(self.z_arr_asc), 3001))
        for i,emu_z in enumerate(self.z_arr_asc):
            HMF_interp_input[i,:len(emu_dict[emu_z]['HMF'])] = np.log(emu_dict[emu_z]['HMF'])
        HMF_interp = RectBivariateSpline(self.z_arr_asc, np.linspace(13, 16, 3001), HMF_interp_input, kx=1, ky=1)

        if get_errors:
            HMFerr_interp_input = np.zeros((len(self.z_arr_asc), 3001))
            for i,emu_z in enumerate(self.z_arr_asc):
                HMFerr_interp_input[i,:len(emu_dict[emu_z]['HMF_std'])] = emu_dict[emu_z]['HMF_std']
            HMFerr_interp = RectBivariateSpline(self.z_arr_asc, np.linspace(13, 16, 3001), HMFerr_interp_input, kx=1, ky=1)


        # Call interpolation at input z and m
        HMF_out = np.exp(HMF_interp(z, np.log10(m)))

        HMFerr_out = np.zeros((len(z), len(m)))
        if get_errors:
            # First interpolate to requested m
            HMFerr_at_m = HMFerr_interp(self.z_arr_asc, np.log10(m))
            # Now add weighted errors in quadrature
            for z_id,this_z in enumerate(z):
                z_id_nearest = np.argsort(np.abs(self.z_arr_asc-this_z))[:2]
                Delta_z = (this_z - self.z_arr_asc[z_id_nearest])/np.diff(self.z_arr_asc[z_id_nearest])
                HMFerr_out[z_id] = np.sqrt((HMFerr_at_m[z_id_nearest[0],:]*Delta_z[0])**2 + (HMFerr_at_m[z_id_nearest[1],:]*Delta_z[1])**2)

        return HMF_out, HMFerr_out




    def predict_raw_emu(self, requested_cosmology, N_draw=0, return_draws=False):
        """Emulates the halo mass function dn/dlnM for the desired set of
        cosmology parameters and returns an output dictionary. This function
        allows the user to have more fine-grained control over the raw emulator
        output.

        :param requested_cosmology: The set of cosmology parameters for which
            the mass function is requested. The parameters are `Ommh2`, `Ombh2`,
            `Omnuh2`, `n_s`, `h`, `sigma_8`, `w_0`, `w_a`.
        :type requested_cosmology: dict

        :param N_draw: The emulator can provide error estimates for its mass
            function prediction. If `N_draw` is provided, the emulator also
            provides `N_draw` samples of the mass function and the standard
            deviation of those estimates.
        :type N_draw: int, optional

        :param return_draws: If True, also return the mass function draws from
            the emulator posterior distribution. Default is False to save
            memory. Applies only if `N_draw` is > 0.
        :type return_draws: bool, optional

        :returns: A dictionary containing all the emulator output. A `readme`
            key describes the units: The mass functions are dn/dlnM [(h/Mpc)^3].
            The output is organized by redshift -- each dictionary key
            corresponds to one redshift. For each redshift, the output contains
            the following data:

            redshift: float
                The redshift of the emulator output.
            log10_M: array_like
                Decadic logarithm log10(mass [Msun/h]) for which the mass
                function is emulated.
            HMF: array_like
                The mass function corresponding to the mean emulated parameters.
            HMF_mean: array_like, optional
                The mass function corresponding to the mean of the mass
                functions drawn from the emulator posterior distribution. Only
                if `N_draw` is > 0.
            HMF_std: array_like, optional
                The (relative) standard deviation in the mass function draws
                from the emulator posterior distribution. Should be used as a
                relative error on the mass function. Only if `N_draw` is > 0.
            HMF_draws: ndarray, optional
                Mass function realizations drawn from the emulator posterior
                distribution. The return values `HMF_mean` and `HMF_std` are
                computed from these. Only if `N_draw` is > 0 and if
                `return_draws` is True.
        :rtype: dict
        """
        # Validate and normalize requested cosmology
        requested_cosmology_normed = self.__normalize_params(requested_cosmology)

        output = {'Units': "log10_M is log10(Mass in [Msun/h]), HMFs are given in dn/dlnM [(h/Mpc)^3]"}
        log10_M_full = np.linspace(13, 16, 3001)
        for i,emu_z in enumerate(self.z_arr):
            output[emu_z] = {'redshift': emu_z,
                                     'log10_M': log10_M_full[:len(self.__PCA_means[i])],}

            # Call the GP
            wstar, wstar_covmat = self.__GPreg[i].predict(requested_cosmology_normed)
            wstar_covmat*= self.__facs[i]
            # De-standardize to GP input
            PC_weight = wstar * self.__GP_std[i] + self.__GP_means[i]
            # PCA transform
            output[emu_z]['HMF'] = np.exp(np.dot(PC_weight, self.__PCA_transform[i]) + self.__PCA_means[i])

            # Draw parameter realizations
            if N_draw>0:
                wstar_draws = np.random.multivariate_normal(wstar, wstar_covmat, N_draw)
                PC_weight_draws = wstar_draws * self.__GP_std[i] + self.__GP_means[i]
                HMF_draws = np.exp(np.dot(PC_weight_draws, self.__PCA_transform[i]) + self.__PCA_means[i])
                # Replace infinites with nan to be able to get mean and std
                idx = [np.all(np.isfinite(HMF_draws[j])) for j in range(N_draw)]
                output[emu_z]['HMF_draws'] = HMF_draws[idx]
                # Compute statistics
                output[emu_z]['HMF_mean'] = np.mean(output[emu_z]['HMF_draws'], axis=0)
                output[emu_z]['HMF_std'] = np.std(output[emu_z]['HMF_draws']/output[emu_z]['HMF_mean'], axis=0)
                if not return_draws:
                    del output[emu_z]['HMF_draws']

        return output


    def __translate_params(self, cosmo_dict):
        """Copy cosmology parameter variables defined without underscores to
        variable names with underscore, which is the default naming scheme. If
        both variable flavors are provided, check for consistency.

        :param cosmo_dict: The input set of cosmology parameters.
        :type cosmo_dict: dict

        :return: Whether duplicate variables are consistent or not.
        :rtype: bool
        """
        for var_w, var_wo in zip(['w_0', 'w_a', 'n_s', 'sigma_8'], ['w0', 'wa', 'ns', 'sigma8']):
            if var_wo in cosmo_dict.keys():
                if var_w in cosmo_dict.keys():
                    if not np.isclose(cosmo_dict[var_wo], cosmo_dict[var_w]):
                        return False
                else:
                    cosmo_dict[var_w] = cosmo_dict[var_wo]
        return True


    def validate_params(self, cosmo_dict):
        """Validate that a given input cosmology dictionary is complete and
        within the bounds of the Mira-Titan Universe design. Note that this
        function is only there for user convenience and is not called by the
        emulator code (which will raise an error and explain its cause).

        :param cosmo_dict: The set of cosmology parameters to validate.
        :type cosmo_dict: dict

        :return: Whether the provided dictionary is valid or not.
        :rtype: bool
        """
        # Translate parameter names where necessary
        if not self.__translate_params(cosmo_dict):
            return False
        # Validate joint limit in w_0, w_a, then add w_b
        for param in ['w_0', 'w_a']:
            if param not in cosmo_dict.keys():
                return False
        if cosmo_dict['w_a'] > -cosmo_dict['w_0']:
            return False
        cosmo_dict['w_b'] = (-cosmo_dict['w_0'] - cosmo_dict['w_a'])**.25
        # Check all keys and parameter ranges
        for param in self.param_limits.keys():
            if param not in cosmo_dict.keys():
                return False
            if cosmo_dict[param]<self.param_limits[param][0]:
                return False
            if cosmo_dict[param]>self.param_limits[param][1]:
                return False
        return True


    def __normalize_params(self, cosmo_dict):
        """Check that a given input cosmology dictionary is complete and within
        the bounds of the Mira-Titan Universe design and return the normalized
        cosmological parameter array."""
        # Translate parameter names where necessary
        if not self.__translate_params(cosmo_dict):
            raise ValueError("At least one variable is provided twice but with inconsistent values")
        # Validate joint limit in w_0, w_a, then add w_b
        for param in ['w_0', 'w_a']:
            if param not in cosmo_dict.keys():
                raise KeyError("You did not provide %s"%param)
        if cosmo_dict['w_a'] > -cosmo_dict['w_0']:
            raise ValueError("w_0 + w_a must be <0. You have w_0 %.4f and w_a %.4f"%(cosmo_dict['w_0'], cosmo_dict['w_a']))
        cosmo_dict['w_b'] = (-cosmo_dict['w_0'] - cosmo_dict['w_a'])**.25
        # Check keys and parameter ranges
        for param in self.param_limits.keys():
            if param not in cosmo_dict.keys():
                raise KeyError("You did not provide %s"%param)
            if cosmo_dict[param]<self.param_limits[param][0]:
                raise ValueError("Parameter %s is %.4f but must be >= %.4f"%(param, cosmo_dict[param], self.param_limits[param][0]))
            if cosmo_dict[param]>self.param_limits[param][1]:
                raise ValueError("Parameter %s is %.4f but must be <= %.4f"%(param, cosmo_dict[param], self.param_limits[param][1]))
        # Normalize the parameters
        normed_p = np.empty(len(self.param_limits.keys()))
        for i,param in enumerate(self.param_limits.keys()):
            normed_p[i] = (cosmo_dict[param] - self.param_limits[param][0]) / (self.param_limits[param][1] - self.param_limits[param][0])

        return normed_p
