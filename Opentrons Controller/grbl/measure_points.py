import numpy as np
from robot import robot

import time

import usbtmc as backend
import pyTHM1176.api.thm_usbtmc_api as thm_api

import utilities

# Get valid points and origin info from latest read
valid_points = utilities.read_points("valid_points.csv")
#valid_points = valid_points[valid_points[:,0]>150]
origin_info = utilities.read_points("origin_info.csv")

# Extract origin and orientation from origin_info
origin = origin_info[0]  # The origin position
rotation_matrix = origin_info[1:4]  # The unit vectors for X, Y, and Z directions (3x3 matrix)

# Translate valid points to origin's reference frame
translated_points = valid_points - origin

# Apply the rotation matrix to align the points with the global reference frame
true_coordinates = translated_points @ rotation_matrix.T  # Matrix multiplication with the transpose of the rotation matrix

field_vals = np.zeros_like(true_coordinates)

utilities.connect_robot()
utilities.connect_probe()

robot.move_head(y=valid_points[0,1], z=valid_points[0,2])

for i in range(len(true_coordinates)):
    target = valid_points[i]
    print(target)
    utilities.move_to(target)
    time.sleep(0.1)
    field_vals[i,:] = utilities.read_field()
    print(f"Measured field: \t{field_vals[i,0]:.3f}\t{field_vals[i,1]:.3f}\t{field_vals[i,2]:.3f}")


utilities.save_readings(true_coordinates, field_vals, "field_readings.csv")