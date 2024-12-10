import numpy as np
from robot import robot
from scipy.optimize import least_squares

import time

import usbtmc as backend
import pyTHM1176.api.thm_usbtmc_api as thm_api

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


def read_points(filename):
    # Read the CSV file into a NumPy array
    points = np.loadtxt(filename, delimiter=",", skiprows=1)  # Skip the header row
    return points

def save_points(filename, points):
    # Save calibration points to CSV
    headers = "X[mm],Y[mm],Z[mm]"
    np.savetxt(filename, points, delimiter=",", header=headers, comments="")

def connect_probe():
    global params
    global thm

    # Parameters of the THM1176 probe
    params = {"trigger_type": "single", 'range': '0.1T', 'average': 30000, 'format': 'ASCII'}

    # Connect to the first probe in the list of devices
    thm = thm_api.Thm1176(backend.list_devices()[0], **params)

    # Get device id string and print output. This can be used to check communications are OK
    device_id = thm.get_id()
    for key in thm.id_fields:
        print('{}: {}'.format(key, device_id[key]))

def connect_robot():
    # Connect to robot
    robot.connect("COM6")
    # Home robot to prevent misalignment
    robot.home()

def home_robot():
    # Home robot
    robot.home()

def move_to(point):
    # Move robot to an absolute position
    robot.move_head(x=point[0], y=point[1], z=point[2])

def get_position():
    # Get the current position of the robot
    pos = np.array(robot.pos)
    return pos

def move_relative(point):
    # Move to position relative to current position
    pos = get_position() + np.array(point)
    print(f"moving to {pos}")
    move_to(pos)

def read_field():
    thm.make_measurement(**params)
    meas = thm.last_reading
    measurements = list(meas.values())

    # Readings in mT aligned with bore coordinates
    Bx = np.array(measurements[2])*1000     # Z-axis of probe points along positive X-axis of bore
    By = np.array(measurements[1])*-1000    # Y-axis of probe points along negative Y-axis of bore
    Bz = np.array(measurements[0])*1000     # X-axis of probe points along positive Z-axis of bore

    return np.array([Bx, By, Bz]).flatten()

def save_readings(coords, readings, filename):
    # Horizontally stack the coordinates and readings
    data = np.hstack((coords, readings))
    
    # Define column headers
    headers = "X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]"
    
    # Save to CSV with headers
    np.savetxt(filename, data, delimiter=",", header=headers, comments="")

# Define residual function for cylinder with fixed x-axis
def cylinder_residuals(params, points):
    # Parameters: (center_y, center_z, radius)
    center_y, center_z, radius = params
    
    residuals = []
    for point in points:
        # Distance in the yz-plane from the point to the cylinder center
        distance = np.sqrt((point[1] - center_y) ** 2 + (point[2] - center_z) ** 2) - radius
        residuals.append(distance)
    
    return residuals

def fit_cylinder(points):
    # Initial guess for cylinder center and radius
    initial_center_y = np.mean(points[:, 1])
    initial_center_z = np.mean(points[:, 2])
    initial_radius = bore_radius
    initial_guess = [initial_center_y, initial_center_z, initial_radius]

    # Optimize the cylinder parameters
    result = least_squares(cylinder_residuals, initial_guess, args=(points,))
    fitted_params = result.x
    fitted_center_y = fitted_params[0]
    fitted_center_z = fitted_params[1]
    fitted_radius = fitted_params[2]

    # Print the fitted cylinder parameters
    print(f"Fitted Cylinder Center (y, z): ({fitted_center_y}, {fitted_center_z})")
    print(f"Fitted Cylinder Radius: {fitted_radius}")

    return fitted_params

def linear_distance(x1, x2):
    return np.abs(x1-x2)

def points_in_cuboid(points, x, y, z, l, w, h):
    X = points[:,0]
    Y = points[:,1]
    Z = points[:,2]
    mask = (linear_distance(X,x) <= l/2) & (linear_distance(Y,y) <= w/2) & (linear_distance(Z,z) <= h/2)

    return points[mask]

def absolute_distance(p1, p2):
    # Calculate the Euclidean distance between points p1 and p2
    return np.sqrt(np.sum((p1 - p2) ** 2, axis=1))

def points_in_cylinder(points, x, y, z, r, l):
    X = points[:,0]
    Y = points[:,1]
    Z = points[:,2]

    P1 = points
    P2 = np.vstack([X,np.zeros_like(X)+y,np.zeros_like(X)+z]).T

    mask = (absolute_distance(P1,P2) <= r) & (linear_distance(X,x) <= l/2)

    points = points[mask]

    return points

def points_in_sphere(points,x,y,z,r):
    center = np.array(x,y,z)
    mask = (absolute_distance(points, center) <=r)

    points = points[mask]

    return points

def get_valid_points_cartesian(x, y, z, r, l=bore_length, clearance=20, spacing=10):
    # Generate X, Y, Z ranges
    X = np.arange(opentrons_x_range[0], opentrons_x_range[1], spacing)
    Y = np.arange(opentrons_y_range[0], opentrons_y_range[1], spacing)
    Z = np.arange(opentrons_z_range[0], opentrons_z_range[1], spacing)
    
    # Create a meshgrid of all possible points
    X_grid, Y_grid, Z_grid = np.meshgrid(X, Y, Z, indexing='ij')
    
    # Flatten grids to a list of points
    points = np.vstack([X_grid.ravel(), Y_grid.ravel(), Z_grid.ravel()]).T
    
    # Points in cylinder of bore radius minus clearance
    valid_points = points_in_cylinder(points,x,y,z,r-clearance,l)
    
    return valid_points

