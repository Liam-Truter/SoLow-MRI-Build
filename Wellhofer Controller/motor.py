import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class Motor:
    def __init__(self, motor=0, pot=0):
        self.motor = motor
        self.pot = pot
    
    def linear_model(self, x, a, b):
        return a * x + b

    def logarithmic_model(self, x, a, b, p):
        return a * np.log(x + p) + b

    def constrained_ransac_fit(self, model='linear'):
        best_inliers = 0
        best_params = None
        n_trials = 100  # Number of random trials
        threshold = 100  # Threshold for inlier classification
        range_check_x = np.linspace(0, 9, 100)  # Points to check for positivity

        for _ in range(n_trials):
            # Select a random sample of three points
            sample_indices = np.random.choice(len(self.distances), 3, replace=False)
            x_sample = np.array(self.distances)[sample_indices]
            y_sample = np.array(self.resistances)[sample_indices]

            # Select the model to fit to the points
            if self.model == 'linear':
                model_func = self.linear_model
            elif self.model == 'log' or model == 'logarithmic':
                model_func = self.logarithmic_model
            
            # Fit the model to the random sample with positivity constraint
            try:
                params, _ = curve_fit(
                    model_func, x_sample, y_sample, 
                    p0=[1, 1, 1],
                    bounds=([0, 0, 0], [np.inf, np.inf, np.inf])  # Enforcing positive parameters
                )
            except RuntimeError:
                continue  # Skip if fitting fails

            # Check if the fitted model meets the positivity constraint over [0, 9]
            y_check = model_func(range_check_x, *params)

            if np.min(y_check) <= 0:
                continue  # Skip this model if it goes below zero

            # Calculate inliers based on threshold
            y_pred = model_func(np.array(self.distances), *params)
            residuals = np.abs(np.array(self.resistances) - y_pred)
            inliers = residuals < threshold
            n_inliers = np.sum(inliers)

            # Update the best model if this one has more inliers
            if n_inliers > best_inliers:
                best_inliers = n_inliers
                best_params = params
                self.inlier_mask = inliers
                self.outlier_mask = np.logical_not(inliers)

        # Store the best model parameters
        if best_params is not None:
            self.params = best_params
            self.success = True
        else:
            self.success = False

    def calibrate_pot(self, resistances, distances, model='linear'):
        self.resistances = resistances
        self.distances = distances
        self.model = model
        if model in ['log', 'logarithmic', 'linear']:
            self.constrained_ransac_fit(model)
        else:
            raise NotImplementedError("Only logarithmic and linear RANSAC are implemented here.")
    
    def get_position(self, resistance):
        if self.success and (self.model == 'log' or self.model == 'logarithmic'):
            a, b, p = self.params
            return np.exp((resistance - b) / a) - p
        elif self.success and self.model == 'linear':
            a,b = self.params
            return (resistance - b)/a
        else:
            raise ValueError("Fit was unsuccessful, cannot compute position.")
    
    def set_position(self, position):
        if self.success and (self.model == 'log' or self.model == 'logarithmic'):
            a, b, p = self.params
            return self.logarithmic_model(position, a, b, p)
        elif self.success and self.model == 'linear':
            a,b = self.params
            return self.linear_model(position, a, b)

if __name__ == '__main__':
    motor = Motor()

    # Example data with potential outliers
    X = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    R = [306, 880, 1525, 2376, 2965, 3390, 3650, 3894, 4089, 4192]

    # Perform RANSAC calibration with constraint
    motor.calibrate_pot(R, X, 'log')
    if motor.success:
        print("Fitted Parameters:", motor.params)

        # Plotting results
        X_plot = np.linspace(0, 9, 100)
        R_plot = motor.set_position(X_plot)

        plt.figure(figsize=(8, 6))
        plt.plot(X_plot, R_plot, label="Best Fit")
        plt.scatter(np.array(X)[motor.inlier_mask], np.array(R)[motor.inlier_mask], color="blue", label="Inliers")
        plt.scatter(np.array(X)[motor.outlier_mask], np.array(R)[motor.outlier_mask], color="red", label="Outliers")
        plt.xlabel("Distance (X)")
        plt.ylabel("Resistance (R)")
        plt.legend()
        plt.show()
    else:
        print("Fitting failed.")
