import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Data
distances = np.array([0, 15, 22, 32, 41, 49, 58, 64, 74, 83, 94, 102, 115, 125, 134, 142, 
                      151, 159, 167, 174, 181, 190, 199, 206, 214, 222, 227, 238, 248]).reshape(-1, 1)
voltages = np.array([4.910, 4.769, 4.698, 4.604, 4.514, 4.427, 4.340, 4.280, 4.177, 4.090, 
                     3.979, 3.899, 3.766, 3.666, 3.586, 3.505, 3.414, 3.330, 3.254, 3.183, 
                     3.111, 3.018, 2.939, 2.863, 2.792, 2.710, 2.651, 2.547, 2.442])

# Adjust voltage values
adjusted_voltages = 4.998 - voltages

# Fit a linear model to the adjusted voltages and distances
model = LinearRegression()
model.fit(adjusted_voltages.reshape(-1, 1), distances)
slope = model.coef_[0]

# Predicted distances based on the line of best fit
predicted_distances = model.predict(adjusted_voltages.reshape(-1, 1))

# Calculate errors (actual distance - predicted distance)
position_errors = distances.flatten() - predicted_distances.flatten()

# Calculate RMSE
position_rmse = np.sqrt(mean_squared_error(distances, predicted_distances))

# Calculate minimum and maximum errors
min_error = np.min(position_errors)
max_error = np.max(position_errors)

# Plotting the distance vs. adjusted voltage with line of best fit
plt.figure(figsize=(10, 6))
plt.scatter(adjusted_voltages, distances, color='blue', label='Measured Positions')
plt.plot(adjusted_voltages, predicted_distances, color='red', label='Best Fit Line')
plt.xlabel("Adjusted Voltage (V)")
plt.ylabel("Distance (mm)")
plt.title("Distance vs. Adjusted Voltage with Line of Best Fit")
plt.legend()
plt.grid(True)
plt.show()

# Displaying the RMSE and error distribution
print(f"Position RMSE: {position_rmse:.3f} mm")
print(f"Minimum Error: {min_error:.3f} mm")
print(f"Maximum Error: {max_error:.3f} mm")

# Plotting the distribution of errors
plt.figure(figsize=(10, 6))
plt.hist(position_errors, bins=10, color='purple', edgecolor='black')
plt.xlabel("Position Error (mm)")
plt.ylabel("Frequency")
plt.title("Distribution of Position Errors")
plt.grid(True)
plt.show()

# Calculate the volts per mm based on the slope of the line of best fit
volts_per_mm = abs(4.998/slope[0])  # Using the slope's magnitude for volts per mm

# Define the target resolution for position (e.g., 0.1 mm) and the ADC reference voltage (5V)
target_distance_resolution = 0.1  # Desired resolution in mm
v_ref = 5.0  # Reference voltage of 5V for the ADC

# Calculate the required voltage resolution for 0.1 mm distance resolution
required_voltage_resolution = volts_per_mm * target_distance_resolution

# Calculate the number of ADC levels needed to achieve this voltage resolution
adc_levels_needed = v_ref / required_voltage_resolution

# Calculate the number of bits required (log2 of adc_levels_needed, rounded up)
bits_needed = int(np.ceil(np.log2(adc_levels_needed)))

# Output results
print(f"Volts per mm: {volts_per_mm:.5f} V/mm")
print(f"Required voltage resolution for 0.1 mm: {required_voltage_resolution:.5f} V")
print(f"Bits needed for sub-millimeter resolution: {bits_needed} bits")

