import pandas as pd

# Function to transform the columns
def transform_columns(input_file, output_file, invert):
    # Read the CSV file
    data = pd.read_csv(input_file)

    if invert:
        factor = -1
    else:
        factor = 1

    # Perform the transformations
    transformed_data = pd.DataFrame({
        'R': factor * data['R'],  # R remains unchanged
        'Bx': data['Bz'],         # Bx = Bz
        'By': -data['By'],        # By = -By
        'Bz': data['Bx']          # Bz = Bx
    })


    # Save the transformed data to a new CSV file
    transformed_data.to_csv(output_file, index=False)
    print(f"Transformed data saved to {output_file}")

coils = ['A', 'B']
angles = [-45, 0, 45, 90]
new_angles = [45, 0, 135, 90]
invert_r = [True, True, True, False]

for coil in coils:
    for i, angle in enumerate(angles):
        # File paths
        input_file = f"Readings\\Gradient coils\\{coil}\\readings_{angle}.csv"  # Replace with your input file path

        new_angle = new_angles[i]

        output_file = f"Readings Corrected\\Gradient coils\\{coil}\\readings_{new_angle}.csv"  # Replace with your desired output file path

        # Transform the columns
        transform_columns(input_file, output_file, invert_r[i])
