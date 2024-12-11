import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

axis = 'z'

# Load the data from the CSV file
file_path = f"field_readings.csv"  # Replace with your actual file path
data = pd.read_csv(file_path)

target_gradients={'x': np.array([0.5774,  0.8165,  0]),
                  'y': [0.5774, -0.4082, -0.7071],
                  'z': np.array([0.5774, -0.4082,  0.7071])}

target_gradient = target_gradients[axis]

# Extract coordinates and magnetic field components
X = data['X[mm]'].values
Y = data['Y[mm]'].values
Z = data['Z[mm]'].values
Bx = -data['Bx[mT]'].values
By = -data['By[mT]'].values
Bz = -data['Bz[mT]'].values

# Filter data where X > -150
mask = X > -30
X = X[mask]
Y = Y[mask]
Z = Z[mask]
Bx = Bx[mask]
By = By[mask]
Bz = Bz[mask]

# Calculate the magnitude of the magnetic field
B_magnitude = np.sqrt(Bx**2 + By**2 + Bz**2)

# Normalize the vectors for quiver plot (optional, for consistent arrow lengths)
Bx_normalized = Bx / B_magnitude
By_normalized = By / B_magnitude
Bz_normalized = Bz / B_magnitude

# --- Figure 1: Magnetic Field Vectors (Quiver Plot) ---
fig1 = plt.figure(figsize=(12, 8))
ax1 = fig1.add_subplot(111, projection='3d')

quiver = ax1.quiver(
    X, Y, Z,
    Bx_normalized, By_normalized, Bz_normalized,
    length=10,  # Arrow length
    normalize=False,
    cmap='viridis',
    linewidth=1,
    alpha=0.8,
    arrow_length_ratio=0.2  # Adjust arrowhead size
)

#ax1.scatter(X,Y,Z)

# Set labels
ax1.set_xlabel("X")
ax1.set_ylabel("Y")
ax1.set_zlabel("Z")
ax1.set_title("Magnetic Field Vectors (Quiver Plot)")

# --- Figure 2: Bz Component Scatter Plot ---
fig2 = plt.figure(figsize=(12, 8))
ax2 = fig2.add_subplot(111, projection='3d')

scatter = ax2.scatter(
    X, Y, Z,
    c=Bz,  # Use Bz as the color value
    cmap='viridis',  # Use a diverging colormap for Bz
    s=50,  # Size of points
    alpha=0.7,
    label="Bz Component"
)

# Add color bar for the scatter plot
cbar = fig2.colorbar(scatter, ax=ax2, pad=0.1)
cbar.set_label('Bz Component (mT)')

# Set labels
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("Z")
ax2.set_title("Actual Bz Component Scatter Plot")

# Expected field given OSI2 gradient from Matlab files
Bz_expected = target_gradient[0]*X + target_gradient[1]*Y + target_gradient[2]*Z

# Reshape Bz_expected for linear regression (needs 2D array for sklearn)
Bz_expected_reshaped = Bz_expected.reshape(-1, 1)

# Perform linear regression to find the optimal scale and offset
model = LinearRegression()
model.fit(Bz_expected_reshaped, Bz)

# Extract scaling factor and offset
scale_factor = model.coef_[0]
offset = model.intercept_

# Adjust Bz_expected to match Bz scale
Bz_expected_scaled = Bz_expected * scale_factor + offset

# --- Figure 3: Expected Bz Component Scatter Plot ---
fig3 = plt.figure(figsize=(12, 8))
ax3 = fig3.add_subplot(111, projection='3d')

scatter = ax3.scatter(
    X, Y, Z,
    c=Bz_expected_scaled,  # Use Bz as the color value
    cmap='viridis',  # Use a diverging colormap for Bz
    s=50,  # Size of points
    alpha=0.7,
    label="Bz Component"
)

# Add color bar for the scatter plot
cbar = fig3.colorbar(scatter, ax=ax3, pad=0.1)
cbar.set_label('Bz Component (mT)')

# Set labels
ax3.set_xlabel("X")
ax3.set_ylabel("Y")
ax3.set_zlabel("Z")
ax3.set_title("Expected Bz Component Scatter Plot")

# Stack coordinates into a matrix
A = np.vstack([X, Y, Z, np.ones_like(X)]).T  # [X, Y, Z, 1] matrix
B = Bz  # Target values (Bz)

# Solve for coefficients [a, b, c, d] using least squares
coefficients, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
a, b, c, d = coefficients

# Gradient vector (a, b, c)
gradient_vector = np.array([a, b, c])*1000
#print(gradient_vector)
gradient_magnitude = np.sqrt(np.sum(gradient_vector**2))

# Normalize the gradient vector
gradient_direction = gradient_vector / np.linalg.norm(gradient_vector)

def format_list(var):
    return f"{var[0]:.3f}, {var[1]:.3f}, {var[2]:.3f}"

# Output results
print(f"Gradient Axis G{axis}")
print(f"Gradient Vector:      {gradient_magnitude:.3f} mT/m")
print(f"Gradient Direction:   {format_list(gradient_direction)}")
print(f"Target Direction:     {format_list(target_gradient)}")
print(f"Direction Error:      {format_list(target_gradient-gradient_direction)}")
print(f"Gradient Sensitivity: {gradient_magnitude/3.22:.3f} mT/m/A", )
# Compute residuals
residuals = Bz - Bz_expected_scaled

# Calculate error metrics
#mae = np.mean(np.abs(residuals))
rmse = np.sqrt(np.mean(residuals**2))
r2 = model.score(Bz_expected_reshaped, Bz)

#print(f"Mean Absolute Error (MAE): {mae:.6f} mT")
print(f"RMSE:                 {rmse:.6f} mT")
print(f"R²:                   {r2:.6f}")

# --- Figure 4: Residuals Scatter Plot ---
fig4 = plt.figure(figsize=(12, 8))
ax4 = fig4.add_subplot(111, projection='3d')

scatter_residuals = ax4.scatter(
    X, Y, Z,
    c=residuals,  # Residuals as color values
    cmap='coolwarm',  # Diverging colormap for positive/negative residuals
    s=50,
    alpha=0.7,
    label="Residuals"
)

# Add color bar
cbar_residuals = fig4.colorbar(scatter_residuals, ax=ax4, pad=0.1)
cbar_residuals.set_label('Residuals (mT)')

# Set labels
ax4.set_xlabel("X [mm]")
ax4.set_ylabel("Y [mm]")
ax4.set_zlabel("Z [mm]")
ax4.set_title("Residuals of Bz (Measured - Expected)")

# --- Figure 5: Linearity Histogram ---
fig5 = plt.figure(figsize=(10, 6))
plt.hist(residuals, bins=30, color='skyblue', edgecolor='k', alpha=0.7)
plt.xlabel("Residuals (mT)")
plt.ylabel("Frequency")
plt.title("Histogram of Bz Residuals")
plt.grid(True)

# Show the plot
plt.show()
