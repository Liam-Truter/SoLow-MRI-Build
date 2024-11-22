import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.animation import FuncAnimation

# Bore dimensions
bore_diameter = 290
bore_radius = bore_diameter / 2
bore_length = 440  # Bore length along the X-axis

# Rectangle dimensions
rect_width = 250
rect_height = 250

# Function to plot a horizontal bore
def plot_bore(ax):
    # Cylinder surface
    x = np.linspace(0, bore_length, 100)  # Length along X-axis
    theta = np.linspace(0, 2 * np.pi, 100)  # Angular points
    theta_grid, x_grid = np.meshgrid(theta, x)
    y = bore_radius * np.cos(theta_grid)
    z = bore_radius * np.sin(theta_grid)
    
    # Plot the cylinder surface
    ax.plot_surface(x_grid, y, z, alpha=0.5, color='gray', edgecolor='none')

# Initialize the 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the bore
plot_bore(ax)

# Add labels
ax.set_xlabel("X-axis (mm) - Bore Length")
ax.set_ylabel("Y-axis (mm) - Bore Width")
ax.set_zlabel("Z-axis (mm) - Bore Height")

# Set limits
ax.set_xlim([0, bore_length])
ax.set_ylim([-bore_radius, bore_radius])
ax.set_zlim([-bore_radius, bore_radius])

# Initialize robot tool position
robot_tool, = ax.plot([], [], [], 'ro', markersize=8)  # Red dot for robot tool

# Function to update robot's position
def update_robot(t):
    # Simulate rectangular motion in the YZ plane
    speed = 50
    period = 4 * (rect_width / speed + rect_height / speed)
    t_mod = t % period

    if t_mod < rect_width / speed:
        x = 0
        y = -rect_width / 2 + t_mod * speed
        z = rect_height / 2
    elif t_mod < rect_width / speed + rect_height / speed:
        x = 0
        y = rect_width / 2
        z = rect_height / 2 - (t_mod - rect_width / speed) * speed
    elif t_mod < 2 * rect_width / speed + rect_height / speed:
        x = 0
        y = rect_width / 2 - (t_mod - rect_width / speed - rect_height / speed) * speed
        z = -rect_height / 2
    else:
        x = 0
        y = -rect_width / 2
        z = -rect_height / 2 + (t_mod - 2 * rect_width / speed - rect_height / speed) * speed

    return [x], [y], [z]

# Function to update the animation
def animate(t):
    x, y, z = update_robot(t)
    robot_tool.set_data(x, y)
    robot_tool.set_3d_properties(z)

# Use FuncAnimation for smooth animation
ani = FuncAnimation(fig, animate, frames=np.arange(0, 1000, 0.1), interval=50)

plt.show()
