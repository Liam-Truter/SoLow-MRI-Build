import pandas as pd

# Function to transform the columns
def transform_columns(input_file, output_file):
    # Read the CSV file
    data = pd.read_csv(input_file)

    # Perform the transformations
    transformed_data = pd.DataFrame({
        'X': data['X'],  # R remains unchanged
        'Y': data['Y'],  # R remains unchanged
        'Z': data['Z'],  # R remains unchanged
        'Bx': data['Bz'],         # Bx = Bz
        'By': -data['By'],        # By = -By
        'Bz': data['Bx']          # Bz = Bx
    })


    # Save the transformed data to a new CSV file
    transformed_data.to_csv(output_file, index=False)
    print(f"Transformed data saved to {output_file}")

coils = ['A', 'B']
angles = [0, 1, 2, 3, 4]

for i, angle in enumerate(angles):
    # File paths
    input_file = f"Readings\\Gradient coils\\C\\readings_{angle}.csv"  # Replace with your input file path

    output_file = f"Readings Corrected\\Gradient coils\\C\\readings_{angle}.csv"  # Replace with your desired output file path

    # Transform the columns
    transform_columns(input_file, output_file)
