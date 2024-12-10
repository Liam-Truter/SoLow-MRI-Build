import pandas as pd

# Function to transform the columns
def transform_columns(input_file, output_file):
    # Read the CSV file
    data = pd.read_csv(input_file)

    # Perform the transformations
    transformed_data = pd.DataFrame({
        'X[mm]': data['X[mm]'],           # X remains unchanged
        'Y[mm]': -data['Z[mm]'],          # Y = -Z
        'Z[mm]': data['Y[mm]'],           # Z = Y
        'Bx[mT]': data['Bz[mT]'],         # Bx = Bz
        'By[mT]': -data['Bx[mT]'],        # By = Bx
        'Bz[mT]': data['By[mT]']          # Bz = By
    })


    # Save the transformed data to a new CSV file
    transformed_data.to_csv(output_file, index=False)
    print(f"Transformed data saved to {output_file}")

# File paths
input_file = "Readings\\Gradient coils\\D\\field_readings.csv"  # Replace with your input file path
output_file = "Readings Corrected\\Gradient coils\\D\\field_readings.csv"  # Replace with your desired output file path

# Transform the columns
transform_columns(input_file, output_file)
