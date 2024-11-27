import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import least_squares

# Bore and Opentrons dimensions
bore_diameter = 290
bore_radius = bore_diameter / 2
bore_length = 440  # Bore length along the X-axis

# Probe dimensions
probe_diameter = 10
probe_radius = probe_diameter / 2

# Opentrons workspace limits
opentrons_x_range = (0, 375)
opentrons_y_range = (0, 250)
opentrons_z_range = (-150, 100)

# Offset between Opentrons origin and bore center
bore_center_offset = np.array([5, 125, -25])  # Example offset (x, y, z)

def generate_random_points(num_points=10, radius_variance=3):
    points = []
    quadrant_angles = [
        [0, np.pi / 2],         # Quadrant I
        [np.pi / 2, np.pi],     # Quadrant II
        [np.pi, 3 * np.pi / 2], # Quadrant III
        [3 * np.pi / 2, 2 * np.pi]  # Quadrant IV
    ]
    
    # Ensure even distribution across quadrants
    points_per_quadrant = num_points // 4
    remaining_points = num_points % 4  # Handle uneven distribution

    for quadrant_idx in range(4):  # Iterate through quadrants
        count = points_per_quadrant + (1 if quadrant_idx < remaining_points else 0)
        for _ in range(count):
            while True:  # Keep trying until a valid point is found
                # Random angle within the current quadrant
                theta = np.random.uniform(quadrant_angles[quadrant_idx][0], quadrant_angles[quadrant_idx][1])
                
                # Random radius with variance
                r = bore_radius - probe_radius + np.random.uniform(-radius_variance, 0)
                
                # Fixed position along the bore's length (X-axis)
                x = bore_center_offset[0]
                
                # Convert cylindrical to Cartesian coordinates
                y = r * np.cos(theta)
                z = r * np.sin(theta)
                
                # Apply offset to account for the Opentrons origin
                point = np.array([x, y, z]) + bore_center_offset
                
                # Check if the point is within Opentrons workspace limits
                if (opentrons_x_range[0] <= point[0] <= opentrons_x_range[1] and
                    opentrons_y_range[0] <= point[1] <= opentrons_y_range[1] and
                    opentrons_z_range[0] <= point[2] <= opentrons_z_range[1]):
                    points.append(point)
                    break  # Exit loop once a valid point is generated

    return np.array(points)


# Generate 200 random points
points = generate_random_points(num_points=4)

# Define residual function for cylinder with fixed x-axis
def cylinder_residuals_fixed_axis(params, points):
    # Parameters: (center_y, center_z, radius)
    center_y, center_z, radius = params
    
    residuals = []
    for point in points:
        # Distance in the yz-plane from the point to the cylinder center
        distance = np.sqrt((point[1] - center_y) ** 2 + (point[2] - center_z) ** 2) - radius
        residuals.append(distance)
    
    return residuals

# Initial guess for cylinder center and radius
initial_center_y = np.mean(points[:, 1])
initial_center_z = np.mean(points[:, 2])
initial_radius = bore_radius
initial_guess = [initial_center_y, initial_center_z, initial_radius]

# Optimize the cylinder parameters
result = least_squares(cylinder_residuals_fixed_axis, initial_guess, args=(points,))
fitted_params = result.x
fitted_center_y = fitted_params[0]
fitted_center_z = fitted_params[1]
fitted_radius = fitted_params[2]

# Print the fitted cylinder parameters
print(f"Fitted Cylinder Center (y, z): ({fitted_center_y}, {fitted_center_z})")
print(f"Fitted Cylinder Radius: {fitted_radius}")

# Plot the points and the fitted cylinder
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")
ax.scatter(points[:, 0], points[:, 1], points[:, 2], label="Random Points", color="blue", alpha=0.6)

# Generate cylinder points for visualization
theta = np.linspace(0, 2 * np.pi, 100)
x_cylinder = np.linspace(opentrons_x_range[0], opentrons_x_range[1], 50)
theta, x_cylinder = np.meshgrid(theta, x_cylinder)
y_cylinder = fitted_center_y + fitted_radius * np.cos(theta)
z_cylinder = fitted_center_z + fitted_radius * np.sin(theta)

ax.plot_surface(x_cylinder, y_cylinder, z_cylinder, color="red", alpha=0.3, label="Fitted Cylinder")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.title("Cylinder Fitting with Fixed X-Axis")
plt.legend()
plt.show()