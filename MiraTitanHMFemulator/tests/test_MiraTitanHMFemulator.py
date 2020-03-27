import numpy as np
import inspect
import os
import pytest

import MiraTitanHMFemulator

class TestClass:
    z_arr = np.linspace(0, 2.02, 4)
    m_arr = np.logspace(13, 16, 31)

    def test_init(self):
        self.HMFemu = MiraTitanHMFemulator.Emulator()


    def test_validated_params(self):
        HMFemu = MiraTitanHMFemulator.Emulator()
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
        HMFemu = MiraTitanHMFemulator.Emulator()

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
                HMFemu.predict(_cosmo, self.z_arr, self.m_arr)

        with pytest.raises(TypeError):
            HMFemu.predict()


    def test_cosmo_limits(self):
        HMFemu = MiraTitanHMFemulator.Emulator()

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
                HMFemu.predict(_cosmo, self.z_arr, self.m_arr)

        for k in fiducial_cosmo.keys():
            _cosmo = fiducial_cosmo.copy()
            _cosmo[k]-= 2
            with pytest.raises(ValueError):
                HMFemu.predict(_cosmo, self.z_arr, self.m_arr)


    def test_fiducial(self):
        np.random.seed(1328)
        data_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

        HMFemu = MiraTitanHMFemulator.Emulator()

        fiducial_cosmo = {'Ommh2': .3*.7**2,
                          'Ombh2': .022,
                          'Omnuh2': .006,
                          'n_s': .96,
                          'h': .7,
                          'w_0': -1,
                          'w_a': 0,
                          'sigma_8': .8,
                          }

        res = HMFemu.predict(fiducial_cosmo, self.z_arr, self.m_arr)

        # Mass function
        _fname = os.path.join(data_path, 'fid.npy')
        # np.save(_fname, res[0])
        ref = np.load(_fname)
        assert np.all(np.isclose(res[0], ref))

        # Error on mass function
        _fname = os.path.join(data_path, 'fid_err.npy')
        # np.save(_fname, res[1])
        ref = np.load(_fname)
        assert np.all(np.isclose(res[1], ref))


    def test_center(self):
        np.random.seed(1328)
        data_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

        HMFemu = MiraTitanHMFemulator.Emulator()

        mid_cosmo = {}
        for k in ['Ommh2', 'Ombh2', 'Omnuh2', 'n_s', 'h', 'sigma_8', 'w_0', 'w_a']:
            mid_cosmo[k] = .5 * np.sum(HMFemu.param_limits[k])

        res = HMFemu.predict(mid_cosmo, self.z_arr, self.m_arr)

        # Mass function
        _fname = os.path.join(data_path, 'mid.npy')
        # np.save(_fname, res[0])
        ref = np.load(_fname)
        assert np.all(np.isclose(res[0], ref))

        # Error on mass function
        _fname = os.path.join(data_path, 'mid_err.npy')
        # np.save(_fname, res[1])
        ref = np.load(_fname)
        assert np.all(np.isclose(res[1], ref))
