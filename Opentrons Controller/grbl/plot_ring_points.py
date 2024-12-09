import pandas as pd
import matplotlib.pyplot as plt
import os

import numpy as np

# Define the angles and file naming pattern
filename = "field_readings.csv"

# Read the CSV file
df = pd.read_csv(filename)

# Function to create plots for a given column
def plot_ring_vs_theta(column_name, title, ylabel, save_as=None):
    theta = np.arange(0,2*np.pi, np.pi/36)
    plt.figure(figsize=(10, 6))
    plt.plot(theta, df[column_name])
    plt.title(title)
    plt.xlabel("Angle [rad]")
    plt.ylabel(ylabel)
    #plt.legend()
    plt.grid()
    if save_as:
        plt.savefig(save_as)

# Plot Bx vs angle
plot_ring_vs_theta(
    column_name='Bx[mT]',
    title="Magnetic Field Component Bx vs Angle",
    ylabel="Bx (mT)"
)

# Plot By vs angle
plot_ring_vs_theta(
    column_name='By[mT]',
    title="Magnetic Field Component By vs Angle",
    ylabel="By (mT)"
)

# Plot Bz vs angle
plot_ring_vs_theta(
    column_name='Bz[mT]',
    title="Magnetic Field Component Bz vs Angle",
    ylabel="Bz (mT)"
)

plt.show()
