import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

# Function to generate random points near the bore circumference
def generate_random_points(num_points=10, radius_variance=1):
    points = []
    for _ in range(num_points):
        while True:
            # Random angle around the bore circumference
            theta = np.random.uniform(0, 2 * np.pi)
            
            # Random radius within variance of bore radius
            r = bore_radius - probe_radius + np.random.uniform(-radius_variance, 0)
            
            # Random position along the bore's length (X-axis)
            x = np.random.uniform(0, bore_length)
            
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
                break
    
    return np.array(points)

# Generate 200 random points
random_points = generate_random_points(num_points=200)

def generate_valid_volume():
    # Define polar coordinates for the bore
    theta = np.linspace(0, 2 * np.pi, 100)  # Angle around the bore circumference
    x = np.linspace(bore_center_offset[0], opentrons_x_range[1], 50)    # Positions along the bore's length (X-axis)

    # Create a meshgrid for x and theta
    x_grid, theta_grid = np.meshgrid(x, theta, indexing='ij')

    # Calculate the maximum radial distance (r_rect) at each angle (theta)
    r_max_y = (opentrons_y_range[1] - bore_center_offset[1]) / np.abs(np.cos(theta_grid))
    r_max_z = (opentrons_z_range[1] - bore_center_offset[2]) / np.abs(np.sin(theta_grid))
    r_rect = np.minimum(r_max_y, r_max_z)

    # Clip r_rect to be within bore radius limits
    r_rect = np.clip(r_rect, 0, bore_radius - probe_radius)

    # Convert polar coordinates to Cartesian coordinates
    y = r_rect * np.cos(theta_grid) + bore_center_offset[1]
    z = r_rect * np.sin(theta_grid) + bore_center_offset[2]
    x_grid += bore_center_offset[0]

    return x_grid, y, z

# Generate valid points
valid_x, valid_y, valid_z = generate_valid_volume()

# Plotting
def plot_bore_and_points(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Generate cylinder surface (bore)
    x = np.linspace(0, bore_length, 100)
    theta = np.linspace(0, 2 * np.pi, 100)
    theta_grid, x_grid = np.meshgrid(theta, x)
    y = bore_radius * np.cos(theta_grid)
    z = bore_radius * np.sin(theta_grid)
    y += bore_center_offset[1]
    z += bore_center_offset[2]
    x_grid += bore_center_offset[0]
    
    # Plot bore
    ax.plot_surface(x_grid, y, z, color='gray', alpha=0.5, edgecolor='none', label='Bore Surface')

    # Plot valid volume as a scatter plot
    ax.plot_surface(valid_x, valid_y, valid_z, alpha=0.5, color='blue', label='Valid Volume')

    # Plot the random points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], color='red', s=50, label='Random Points')
    
    # Set plot limits
    ax.set_xlim([min(opentrons_x_range[0],bore_center_offset[0]), max(opentrons_x_range[1], bore_center_offset[0] + bore_length)])
    ax.set_ylim([min(opentrons_y_range[0],opentrons_y_range[0]+bore_center_offset[1]-bore_radius), max(opentrons_y_range[1],  bore_center_offset[1] + bore_radius)])
    ax.set_zlim([min(opentrons_z_range[0],opentrons_z_range[0]+bore_center_offset[2]-bore_radius), max(opentrons_z_range[1],  bore_center_offset[2] + bore_radius)])
    
    # Calculate axis ranges
    x_range = np.ptp(ax.get_xlim())
    y_range = np.ptp(ax.get_ylim())
    z_range = np.ptp(ax.get_zlim())
    max_range = max(x_range, y_range, z_range)

    # Center axes
    x_mid = np.mean(ax.get_xlim())
    y_mid = np.mean(ax.get_ylim())
    z_mid = np.mean(ax.get_zlim())

    ax.set_xlim([x_mid - max_range / 2, x_mid + max_range / 2])
    ax.set_ylim([y_mid - max_range / 2, y_mid + max_range / 2])
    ax.set_zlim([z_mid - max_range / 2, z_mid + max_range / 2])

    # Labels and legend
    ax.set_xlabel("X-axis (mm)")
    ax.set_ylabel("Y-axis (mm)")
    ax.set_zlabel("Z-axis (mm)")
    ax.legend()
    plt.show()

# Visualize
plot_bore_and_points(random_points)
