import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = "Readings\\Magnets\\Kian Halbach\\field_readings.csv"  # Replace with your file path
data = pd.read_csv(file_path)

# Extract the relevant data
Y = data["Y[mm]"].values
Z = data["Z[mm]"].values
Bx = data["Bx[mT]"].values
By = data["By[mT]"].values
Bz = data["Bz[mT]"].values

mask = (Y >= -10) & (Y <= 10) & (Z >= -10) & (Z <= 10)
if True:
    Y = Y[mask]
    Z = Z[mask]
    Bx = Bx[mask]
    By = By[mask]
    Bz = Bz[mask]

# Define a function to plot the field and calculate homogeneity
def plot_field(Y, Z, B_field, field_name):
    # Calculate field homogeneity in ppm
    B_mean = np.mean(B_field)
    homogeneity_ppm = np.std(B_field) / B_mean * 1e6  # Standard deviation as ppm of mean
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(Y, Z, c=B_field, cmap="viridis", s=50, edgecolor='k', alpha=0.7)
    
    # Configure axes to point in the desired directions
    ax.invert_xaxis()  # Positive Y to the left
    ax.set_xlabel("Y [mm] (Positive Left)")
    ax.set_ylabel("Z [mm] (Positive Up)")
    ax.set_title(f"{field_name} Field Intensity (mT)\nHomogeneity: {homogeneity_ppm:.2f} ppm")
    
    # Add a color bar
    cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
    cbar.set_label(f"{field_name} Field Intensity (mT)")
    
    plt.grid(True)
    plt.tight_layout()

# Plot each field with homogeneity in ppm
plot_field(Y, Z, Bx, "Bx")
plot_field(Y, Z, By, "By")
plot_field(Y, Z, Bz, "Bz")
plt.show()
