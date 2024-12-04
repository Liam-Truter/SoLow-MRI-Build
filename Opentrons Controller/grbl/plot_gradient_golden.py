import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load the data from the CSV file
file_path = "field_readings.csv"  # Replace with your actual file path
data = pd.read_csv(file_path)

# Extract coordinates and magnetic field components
X = data['X[mm]'].values
Y = data['Y[mm]'].values
Z = data['Z[mm]'].values
Bx = data['Bx[mT]'].values
By = data['By[mT]'].values
Bz = data['Bz[mT]'].values

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
    length=5,  # Arrow length
    normalize=False,
    cmap='viridis',
    linewidth=0.5,
    alpha=0.8,
    arrow_length_ratio=0.2  # Adjust arrowhead size
)

# Set labels
ax1.set_xlabel("X")
ax1.set_ylabel("Y")
ax1.set_zlabel("Z")
ax1.set_title("Magnetic Field Vectors (Quiver Plot)")

# --- Figure 2: Bx Component Scatter Plot ---
fig2 = plt.figure(figsize=(12, 8))
ax2 = fig2.add_subplot(111, projection='3d')

scatter = ax2.scatter(
    X, Y, Z,
    c=Bx,  # Use Bx as the color value
    cmap='coolwarm',  # Use a diverging colormap for Bx
    s=50,  # Size of points
    alpha=0.7,
    label="Bx Component"
)

# Add color bar for the scatter plot
cbar = fig2.colorbar(scatter, ax=ax2, pad=0.1)
cbar.set_label('Bx Component (mT)')

# Set labels
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("Z")
ax2.set_title("Bx Component Scatter Plot")

# Show the plots
plt.show()