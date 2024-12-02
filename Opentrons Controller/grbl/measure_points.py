import numpy as np
from robot import robot

import time

#import usbtmc as backend
#import pyTHM1176.api.thm_usbtmc_api as thm_api

def read_points(filename):
    # Read the CSV file into a NumPy array
    points = np.loadtxt(filename, delimiter=",", skiprows=1)  # Skip the header row
    return points

def connect_probe():
    global params
    global thm

    params = {"trigger_type": "single", 'range': '0.1T', 'average': 30000, 'format': 'ASCII'}

    thm = thm_api.Thm1176(backend.list_devices()[0], **params)
    # Get device id string and print output. This can be used to check communications are OK
    device_id = thm.get_id()
    for key in thm.id_fields:
        print('{}: {}'.format(key, device_id[key]))

def connect_robot():
    robot.connect("COM6")
    robot.home()

def move_to(point):
    robot.move_head(x=point[0], y=point[1], z=point[2])

def read_field():
    thm.make_measurement(**params)
    meas = thm.last_reading
    measurements = list(meas.values())
    Bx = np.array(measurements[0])*1000
    By = np.array(measurements[1])*1000
    Bz = np.array(measurements[2])*1000

    return np.array([Bx, By, Bz])

def save_readings(coords, readings, filename):
    # Horizontally stack the coordinates and readings
    data = np.hstack((coords, readings))
    
    # Define column headers
    headers = "X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]"
    
    # Save to CSV with headers
    np.savetxt(filename, data, delimiter=",", header=headers, comments="")

# Get valid points and origin info from latest read
valid_points = read_points("valid_points.csv")
origin_info = read_points("origin_info.csv")

# Extract origin and orientation from origin_info
origin = origin_info[0]  # The origin position
rotation_matrix = origin_info[1:4]  # The unit vectors for X, Y, and Z directions (3x3 matrix)

# Translate valid points to origin's reference frame
translated_points = valid_points - origin

# Apply the rotation matrix to align the points with the global reference frame
true_coordinates = translated_points @ rotation_matrix.T  # Matrix multiplication with the transpose of the rotation matrix

field_vals = np.zeros_like(true_coordinates)

connect_robot()
#connect_probe()

for i in range(len(true_coordinates)):
    target = valid_points[i]
    print(target)
    move_to(target)
    time.sleep(1)
    #field_vals[i] = read_field()


save_readings(true_coordinates, field_vals, "field_readings.csv")