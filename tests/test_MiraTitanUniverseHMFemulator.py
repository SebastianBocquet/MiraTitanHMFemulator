import numpy as np
import inspect
import os
import pytest

import MiraTitanUniverseHMFemulator

class TestClass:

    def test_init(self):
        self.HMFemu = MiraTitanUniverseHMFemulator.Emulator()


    def test_validated_params(self):
        HMFemu = MiraTitanUniverseHMFemulator.Emulator()
        fiducial_cosmo = {'Ommh2': .3*.7**2,
                          'Ombh2': .022,
                          'Omnuh2': .006,
                          'n_s': .96,
                          'h': .7,
                          'w_0': -1,
                          'w_a': 0,
                          'sigma_8': .8,
                          }
        assert HMFemu.validate_params(fiducial_cosmo) is True

        # Missing keys, parameter limits
        fiducial_cosmo = {'Ommh2': .3*.7**2,
                          'Ombh2': .022,
                          'Omnuh2': .006,
                          'n_s': .96,
                          'h': .7,
                          'w_0': -1,
                          'w_a': 0,
                          'sigma_8': .8,
                          }
        for k in fiducial_cosmo.keys():
            _cosmo = fiducial_cosmo.copy()
            _cosmo.pop(k)
            assert HMFemu.validate_params(_cosmo) is False

            _cosmo = fiducial_cosmo.copy()
            _cosmo[k]+= 2
            assert HMFemu.validate_params(_cosmo) is False

            _cosmo = fiducial_cosmo.copy()
            _cosmo[k]-= 2
            assert HMFemu.validate_params(_cosmo) is False


    def test_missingkey(self):
        HMFemu = MiraTitanUniverseHMFemulator.Emulator()

        fiducial_cosmo = {'Ommh2': .3*.7**2,
                          'Ombh2': .022,
                          'Omnuh2': .006,
                          'n_s': .96,
                          'h': .7,
                          'w_0': -1,
                          'w_a': 0,
                          'sigma_8': .8,
                          }
        for k in fiducial_cosmo.keys():
            _cosmo = fiducial_cosmo.copy()
            _cosmo.pop(k)
            with pytest.raises(KeyError):
                HMFemu.predict(_cosmo)

        with pytest.raises(TypeError):
            HMFemu.predict()


    def test_limits(self):
        HMFemu = MiraTitanUniverseHMFemulator.Emulator()

        fiducial_cosmo = {'Ommh2': .3*.7**2,
                          'Ombh2': .022,
                          'Omnuh2': .006,
                          'n_s': .96,
                          'h': .7,
                          'w_0': -1,
                          'w_a': 0,
                          'sigma_8': .8,
                          }

        for k in fiducial_cosmo.keys():
            _cosmo = fiducial_cosmo.copy()
            _cosmo[k]+= 2
            with pytest.raises(ValueError):
                HMFemu.predict(_cosmo)

        for k in fiducial_cosmo.keys():
            _cosmo = fiducial_cosmo.copy()
            _cosmo[k]-= 2
            with pytest.raises(ValueError):
                HMFemu.predict(_cosmo)


    def test_fiducial(self):
        data_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
        z_arr = [2.02, 1.61, 1.01, 0.656, 0.434, 0.242, 0.101, 0.0]

        HMFemu = MiraTitanUniverseHMFemulator.Emulator()

        fiducial_cosmo = {'Ommh2': .3*.7**2,
                          'Ombh2': .022,
                          'Omnuh2': .006,
                          'n_s': .96,
                          'h': .7,
                          'w_0': -1,
                          'w_a': 0,
                          'sigma_8': .8,
                          }

        res = HMFemu.predict(fiducial_cosmo)

        for i in range(len(z_arr)):
            _fname = os.path.join(data_path, 'fid_%d.npy'%i)
            # np.save(_fname, res[z_arr[i]]['HMF'])
            ref = np.load(_fname)
            assert np.all(np.isclose(ref, res[z_arr[i]]['HMF']))


    def test_center(self):
        data_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
        z_arr = [2.02, 1.61, 1.01, 0.656, 0.434, 0.242, 0.101, 0.0]

        HMFemu = MiraTitanUniverseHMFemulator.Emulator()

        mid_cosmo = {}
        for k in ['Ommh2', 'Ombh2', 'Omnuh2', 'n_s', 'h', 'sigma_8', 'w_0', 'w_a']:
            mid_cosmo[k] = .5 * np.sum(HMFemu.param_limits[k])

        res = HMFemu.predict(mid_cosmo)

        for i in range(len(z_arr)):
            _fname = os.path.join(data_path, 'mid_%d.npy'%i)
            # np.save(_fname, res[z_arr[i]]['HMF'])
            ref = np.load(_fname)
            assert np.all(np.isclose(ref, res[z_arr[i]]['HMF']))
