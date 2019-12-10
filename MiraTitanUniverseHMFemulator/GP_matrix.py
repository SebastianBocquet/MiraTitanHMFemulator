import numpy as np
from scipy import linalg

class GaussianProcess:
    def compute_rho_corr_func_point(self, a, b, this_rho):
        """Compute correlation between two points a and b."""
        corr = np.prod(this_rho**(4 * (a - b)**2))
        return corr


    def compute_rho_corr_func(self, a, b, this_rho):
        """Compute rho correlation function between two vectors a and b.
        Returns kernel matrix [len(a), len(b)]."""
        corr_matrix = [self.compute_rho_corr_func_point(a[i], b[j], this_rho)
            for i in range(a.shape[0]) for j in range(b.shape[0])]
        return np.array(corr_matrix).reshape(a.shape[0], -1)


    def __init__(self, x, y, cov_n, prec_f, rho, compute_lnlike=False):
        """Set up covariance matrix and pre-compute its Cholesky decomposition.
        Parameters
        ----------
            x: design points [N_data, N_dim_input]
            y: design values [N_data, N_output]
            cov_n: covariance of y [N_output*N_data, N_output*N_data]
            prec_f: precision of the GP
            rho: CP correlation length [N_output, N_dim_input]
            compute_lnlike: (optional, default to False) marginal likelihood
        Returns
        -------
            None
        """
        self.N_data = len(x)
        self.N_dim_input = x.shape[1]
        self.N_output = y.shape[1]

        # Check dimensions
        if self.N_data!=len(y):
            raise TypeError("len(design points) %d must match len(design values) %d"%(self.N_data, len(y)))
        if len(prec_f)!=self.N_output:
            raise TypeError("len(prec_f) %d must match number of outputs %d"%(len(prec_f), self.N_output))
        if cov_n.shape!=(self.N_output*self.N_data, self.N_output*self.N_data):
            raise TypeError("Shape of data cov mat (%s,%s) must be (%s,%s)."%(
                cov_n.shape[0], cov_n.shape[1], self.N_output*self.N_data, self.N_output*self.N_data))
        if rho.shape!=(self.N_output, self.N_dim_input):
            raise TypeError("Shape of correlation lengths (%d,%d) must be (%d,%d)"%(
                rho.shape[0], rho.shape[1], self.N_output*self.N_dim_input, self.N_output*self.N_dim_input))

        self.x = x
        self.corr_rho = rho
        self.prec_f = prec_f
        self.y_flat = y.flatten(order='F')

        # Correlation matrix
        self.corrmat = np.zeros((self.N_output*self.N_data, self.N_output*self.N_data))
        for i in range(self.N_output):
            self.corrmat[i*self.N_data:(i+1)*self.N_data, i*self.N_data:(i+1)*self.N_data] = self.compute_rho_corr_func(x, x, self.corr_rho[i])/self.prec_f[i]
        try:
            self.cholesky_factor = linalg.cho_factor(self.corrmat + cov_n)
        except:
            print("Could not compute Cholesky decomposition")
            return
        self.Krig_basis = linalg.cho_solve(self.cholesky_factor, self.y_flat)

        if compute_lnlike:
            chi_squared = np.matmul(self.y_flat.T, self.Krig_basis)
            ln_corrmat_det = 2 * np.sum(np.log(np.diag(self.cholesky_factor[0])))
            self.lnlike = -.5 * chi_squared - .5 * ln_corrmat_det


    def predict(self, x_new):
        """
        Parameters: evaluation points [N_dim_input]
        Returns: (mean, variance)
        """

        if len(x_new)!=self.N_dim_input:
            raise TypeError("Evaluation points %s needs to be shape %d"%(len(x_new), self.N_dim_input))

        # Correlation with design input [N_output, N_data]
        corr_xnew_x = np.zeros((self.N_output, self.N_output*self.N_data))
        for i in range(self.N_output):
            corr_xnew_x[i,i*self.N_data:(i+1)*self.N_data] = [self.compute_rho_corr_func_point(x_new, self.x[j], self.corr_rho[i])
                                                              for j in range(self.N_data)]
        corr_xnew_x/= self.prec_f[:,None]

        # Mean prediction
        eval_mean = np.dot(corr_xnew_x, self.Krig_basis)

        # Variance
        v = linalg.cho_solve(self.cholesky_factor, corr_xnew_x.T)
        eval_covmat = np.diag(1./self.prec_f) - np.dot(corr_xnew_x, v)

        return eval_mean, eval_covmat
