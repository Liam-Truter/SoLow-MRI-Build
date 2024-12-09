import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import least_squares

from calibrator import Calibrator
from robot import robot

# Bore and Opentrons dimensions
bore_diameter = 290
bore_radius = bore_diameter / 2
bore_length = 440  # Bore length along the X-axis

# Probe dimensions
probe_diameter = 10
probe_radius = probe_diameter / 2

# Opentrons workspace limits
opentrons_x_range = (0, 300)
opentrons_y_range = (0, 250)
opentrons_z_range = (-150, 100)

# Offset between Opentrons origin and bore center
bore_center_offset = np.array([5, 125, -25])  # Example offset (x, y, z)

calibrator = Calibrator()

robot.connect("COM6")
robot.home()
calibrator.start()
points = np.array(calibrator.positions)

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
fitted_center_x = points[0,0]
fitted_center_y = fitted_params[0]
fitted_center_z = fitted_params[1]
fitted_radius = fitted_params[2]

# Print the fitted cylinder parameters
print(f"Fitted Cylinder Center (y, z): ({fitted_center_y}, {fitted_center_z})")
print(f"Fitted Cylinder Radius: {fitted_radius}")

def get_valid_points(x, y, z, r, clearance=5, spacing=1):
    # Generate X, Y, Z ranges
    R = r - clearance
    theta = np.arange(0,2*np.pi, np.pi/36)

    X = np.zeros_like(theta) + x
    Y = -R * np.cos(theta) + y
    Z = R * np.sin(theta) + z
    
    # Flatten grids to a list of points
    points = np.vstack([X,Y,Z]).T

    # Filter points within the bore radius and workspace limits
    valid_points = points[
        (opentrons_x_range[0] <= points[:, 0]) & (points[:, 0] <= opentrons_x_range[1]) &
        (opentrons_y_range[0] <= points[:, 1]) & (points[:, 1] <= opentrons_y_range[1]) &
        (opentrons_z_range[0] <= points[:, 2]) & (points[:, 2] <= opentrons_z_range[1])
    ]
    
    return valid_points



# Plot the points and the fitted cylinder
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")
ax.scatter(points[:, 0], points[:, 1], points[:, 2], label="Random Points", color="blue", alpha=0.6)

# Generate cylinder points for visualization
theta = np.linspace(0, 2 * np.pi, 100)
x_cylinder = np.linspace(fitted_center_x, opentrons_x_range[1], 50)
theta, x_cylinder = np.meshgrid(theta, x_cylinder)
y_cylinder = fitted_center_y + fitted_radius * np.cos(theta)
z_cylinder = fitted_center_z + fitted_radius * np.sin(theta)

ax.plot_surface(x_cylinder, y_cylinder, z_cylinder, color="red", alpha=0.3, label="Fitted Cylinder")

valid_points = get_valid_points(points[0,0],fitted_center_y, fitted_center_z, fitted_radius, clearance=80, spacing=10)

def save_points(points, filename="valid_points.csv"):
    # Save the numpy array of points to a CSV file
    header = "X, Y, Z"  # Add column headers
    np.savetxt(filename, points, delimiter=",", header=header, comments='', fmt='%.3f')
    print(f"Valid points saved to {filename}")

# Save to CSV
save_points(valid_points, filename="valid_points.csv")

def get_origin(flipped=False):
    # Origin position. Geometric center of bore
    origin = np.array([fitted_center_x + bore_length/2, fitted_center_y, fitted_center_z])

    # Origin orientation
    x_hat = np.array([1,0,0])
    y_hat = np.array([0,1,0])
    z_hat = np.array([0,0,1])

    # If MRI is rotated
    if flipped:
        
        # Orientation is rotated 180 degrees
        x_hat = -x_hat
        y_hat = -y_hat

    return np.array([origin, x_hat, y_hat, z_hat])
        

save_points(get_origin(), filename="origin_info.csv")

ax.scatter(valid_points[:,0], valid_points[:,1], valid_points[:,2], label="Valid Points", color="red", alpha=0.3)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.title("Cylinder Fitting with Fixed X-Axis")
plt.legend()
plt.show()