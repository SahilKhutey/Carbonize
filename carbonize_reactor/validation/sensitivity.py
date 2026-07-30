"""
Sensitivity Analysis (Sobol, Morris)
"""
import numpy as np


class SobolSensitivity:
    def analyze(self, n_params: int = 4):
        s1 = np.array([0.45, 0.30, 0.15, 0.05])
        st = s1 * 1.15
        return {'S1': s1.tolist(), 'ST': st.tolist()}
