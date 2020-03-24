import numpy as np
import os
import inspect

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
    __param_names = ('Ommh2', 'Ombh2', 'Omnuh2', 'n_s', 'h', 'sigma_8', 'w_0', 'w_b')
    param_limits = {
        'Ommh2': (.12, .155),
        'Ombh2': (.0215, .0235),
        'Omnuh2': (0, .01),
        'n_s': (.85, 1.05),
        'h': (.55, .85),
        'sigma_8': (.7, .9),
        'w_0': (-1.3, -.7),
        'w_a': (-1.73, 1.28),
        'w_b': (.3, 1.3),
    }
    # Emulator redshifts
    z_arr = [2.02, 1.61, 1.01, 0.656, 0.434, 0.242, 0.101, 0.0]



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



    def predict(self, requested_cosmology, N_draw=0, return_draws=False):
        """Emulates the halo mass function dn/dlnM for the desired set of
        cosmology parameters and returns an output dictionary.

        Parameters
        ----------
        requested_cosmology : dictionary
            The set of cosmology parameters for which the HMF is requested. The
            parameters are `Ommh2`, `Ombh2`, `Omnuh2`, `n_s`, `h`,
            `sigma_8`, `w_0`, `w_a`.
        N_draw : int, optional
            The emulator can provide error estimates for its HMF prediction. If
            `N_draw` is provided, the emulator also provides `N_draw`
            samples of the HMF and the standard deviation of those estimates.
        return_draws : bool, optional
            If True, also return the HMF draws from the emulator posterior
            distribution. Default is False to save memory. Applies only if
            `N_draw` is > 0.

        Returns
        -------
        output : dictionary
            A dictionary containing all the emulator output. A `readme` key
            describes the units: The HMFs are dn/dlnM [(h/Mpc)^3]. The output is
            organized by redshift -- each dictionary key corresponds to one
            redshift. For each redshift, the output contains the following data:

        redshift : float
            The redshift of the emulator output.

        log10_M : array
            Decadic logarithm log10(mass [Msun/h]) for which the HMF is
            emulated.

        HMF : array
            The HMF corresponding to the mean emulated parameters.

        HMF_mean : array, optional
            The HMF corresponding to the mean of the HMFs drawn from the
            emulator posterior distribution. Only if `N_draw` is > 0.

        HMF_std : array, optional
            The (relative) standard deviation in the HMF draws from the emulator
            posterior distribution. Should be used if as a relative error on the
            HMF. Only if `N_draw` is > 0.

        HMF_draws : ndarray, optional
            HMF realizations drawn from the emulator posterior distribution. The
            return values `HMF_mean` and `HMF_std` are computed from these. Only
            if `N_draw` is > 0 and if `return_draws` is True.
        """
        # Validate and normalize requested cosmology
        requested_cosmology_normed = self.__normalize_params(requested_cosmology)

        output = {'Units': "log10_M is log10(Mass in [Msun/h]), HMFs are given in dn/dlnM [(h/Mpc)^3]"}
        log10_M_full = np.linspace(13, 16, 3001)
        for i in range(len(self.z_arr)):
            output[self.z_arr[i]] = {'redshift': self.z_arr[i],
                                     'log10_M': log10_M_full[:len(self.__PCA_means[i])],}

            # Call the GP
            wstar, wstar_covmat = self.__GPreg[i].predict(requested_cosmology_normed)
            wstar_covmat*= self.__facs[i]
            # De-standardize to GP input
            PC_weight = wstar * self.__GP_std[i] + self.__GP_means[i]
            # PCA transform
            output[self.z_arr[i]]['HMF'] = np.exp(np.dot(PC_weight, self.__PCA_transform[i]) + self.__PCA_means[i])

            # Draw parameter realizations
            if N_draw>0:
                wstar_draws = np.random.multivariate_normal(wstar, wstar_covmat, N_draw)
                PC_weight_draws = wstar_draws * self.__GP_std[i] + self.__GP_means[i]
                HMF_draws = np.exp(np.dot(PC_weight_draws, self.__PCA_transform[i]) + self.__PCA_means[i])
                # Replace infinites with nan to be able to get mean and std
                idx = [np.all(np.isfinite(HMF_draws[j])) for j in range(N_draw)]
                output[self.z_arr[i]]['HMF_draws'] = HMF_draws[idx]
                # Compute statistics
                output[self.z_arr[i]]['HMF_mean'] = np.mean(output[self.z_arr[i]]['HMF_draws'], axis=0)
                output[self.z_arr[i]]['HMF_std'] = np.std(output[self.z_arr[i]]['HMF_draws']/output[self.z_arr[i]]['HMF_mean'], axis=0)
                if not return_draws:
                    del output[self.z_arr[i]]['HMF_draws']

        return output


    def validate_params(self, cosmo_dict):
        """Validate that a given input cosmology dictionary is complete and
        within the bounds of the Mira-Titan Universe design. Note that this
        function is only there for user convenience and is not called by the
        emulator code (which will raise an error and explain its cause).

        Parameters
        ----------
        cosmo_dict : dictionary
            The set of cosmology parameters to validate.

        Returns
        -------
        valid : bool
            Whether the provided dictionary is valid or not.
        """
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
        normed_p = np.empty(len(self.__param_names))
        for i,param in enumerate(self.__param_names):
            normed_p[i] = (cosmo_dict[param] - self.param_limits[param][0]) / (self.param_limits[param][1] - self.param_limits[param][0])

        return normed_p
