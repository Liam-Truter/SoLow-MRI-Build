import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the angles and file naming pattern
quadrants = [0, 1, 2, 3, 4]
coil = 'C'
file_pattern = "Readings\\Gradient coils\\{coil}\\readings_{quadrant}.csv"

# Prepare a dictionary to store the data for plotting
data = {}

# Read the CSV files and store data for each angle
for quadrant in quadrants:
    filename = file_pattern.format(coil=coil, quadrant=quadrant)
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        data[quadrant] = df
    else:
        print(f"File {filename} not found. Skipping this quadrant.")

# Function to create plots for a given column
def plot_column_vs_r(column_name, title, ylabel, save_as=None):
    plt.figure(figsize=(10, 6))
    for quadrant in data:
        df = data[quadrant]
        plt.plot(df['X'], df[column_name], label=f"Quadrant {quadrant}°")
    plt.title(title)
    plt.xlabel("X [mm]")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()
    if save_as:
        plt.savefig(save_as)

# Plot Bx vs R
plot_column_vs_r(
    column_name='Bx',
    title="Magnetic Field Component Bx vs Distance",
    ylabel="Bx (mT)"
)

# Plot By vs R
plot_column_vs_r(
    column_name='By',
    title="Magnetic Field Component By vs Distance",
    ylabel="By (mT)"
)

# Plot Bz vs R
plot_column_vs_r(
    column_name='Bz',
    title="Magnetic Field Component Bz vs Distance",
    ylabel="Bz (mT)"
)

plt.show()
