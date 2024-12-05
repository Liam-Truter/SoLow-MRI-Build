import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the angles and file naming pattern
angles = [0, 45, 90, 135]
coil = 'B'
file_pattern = "Readings Corrected\\Gradient coils\\{coil}\\readings_{angle}.csv"

# Prepare a dictionary to store the data for plotting
data = {}

# Read the CSV files and store data for each angle
for angle in angles:
    filename = file_pattern.format(coil=coil, angle=angle)
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        data[angle] = df
    else:
        print(f"File {filename} not found. Skipping this angle.")

# Function to create plots for a given column
def plot_column_vs_r(column_name, title, ylabel, save_as=None):
    plt.figure(figsize=(10, 6))
    for angle in data:
        df = data[angle]
        plt.plot(df['R'], df[column_name], label=f"Angle {angle}°")
    plt.title(title)
    plt.xlabel("R (radius)")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()
    if save_as:
        plt.savefig(save_as)

# Plot Bx vs R
plot_column_vs_r(
    column_name='Bx',
    title="Magnetic Field Component Bx vs Radius",
    ylabel="Bx (mT)"
)

# Plot By vs R
plot_column_vs_r(
    column_name='By',
    title="Magnetic Field Component By vs Radius",
    ylabel="By (mT)"
)

# Plot Bz vs R
plot_column_vs_r(
    column_name='Bz',
    title="Magnetic Field Component Bz vs Radius",
    ylabel="Bz (mT)"
)

plt.show()
