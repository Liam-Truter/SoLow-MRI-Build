import csv

def read_coordinates_from_csv(file_path):
    """
    Reads coordinates from a CSV file.
    The CSV is expected to have three columns: X, Y, Z.
    """
    coordinates = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            try:
                x, y, z = map(float, row)
                coordinates.append((x, y, z))
            except ValueError:
                # Skip rows that don't have valid numerical coordinates
                continue
    return coordinates

def write_gcode_file(coordinates, output_path, feed_rate=1500):
    """
    Writes a G-code file to move to each coordinate.
    
    Parameters:
        coordinates: List of tuples (X, Y, Z).
        output_path: Path to save the G-code file.
        feed_rate: Movement speed in mm/min.
    """
    with open(output_path, mode='w') as file:
        file.write("; G-code generated from CSV coordinates\n")
        file.write("G21 ; Set units to millimeters\n")
        file.write("G90 ; Use absolute positioning\n")
        file.write("G28 ; Home all axes\n")
        file.write("\n")
        
        for coord in coordinates:
            x, y, z = coord
            x = x - 377
            y = y - 252
            z = z - 252
            file.write(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed_rate}\n")
        
        file.write("\n; End of G-code\n")

def main():
    # File paths
    input_csv_path = "valid_points.csv"  # Input CSV file with coordinates
    output_gcode_path = "output.gcode"  # Output G-code file
    
    # Read coordinates from the CSV file
    coordinates = read_coordinates_from_csv(input_csv_path)
    
    # Write G-code file
    write_gcode_file(coordinates, output_gcode_path)
    print(f"G-code file written to {output_gcode_path}")

if __name__ == "__main__":
    main()
