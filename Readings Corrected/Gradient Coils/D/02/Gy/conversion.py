import pandas as pd
import numpy as np

def rotate_about_z(input_file, output_file, theta):
    # Read the CSV file
    data = pd.read_csv(input_file)

    # Extract coordinates
    X = data['X[mm]'].values
    Y = data['Y[mm]'].values
    Z = data['Z[mm]'].values

    # Compute the rotation matrix
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    # Apply the rotation
    X_new = cos_theta * X - sin_theta * Y
    Y_new = sin_theta * X + cos_theta * Y

    # Create the transformed DataFrame
    transformed_data = pd.DataFrame({
        'X[mm]': X_new,
        'Y[mm]': Y_new,
        'Z[mm]': Z,  # Z remains unchanged
        'Bx[mT]': data['Bx[mT]'],
        'By[mT]': data['By[mT]'],
        'Bz[mT]': data['Bz[mT]']
    })

    # Save the transformed data to a new CSV file
    transformed_data.to_csv(output_file, index=False)
    print(f"Transformed data saved to {output_file}")

# File paths
input_file = "Readings\\Gradient coils\\D\\02\\Gy\\field_readings.csv"  # Replace with your input file path
output_file = "Readings Corrected\\Gradient coils\\D\\02\\Gy\\field_readings.csv"  # Replace with your desired output file path

# Rotation angle in radians
theta = 5*-0.02069

# Perform the rotation
rotate_about_z(input_file, output_file, theta)
