import numpy as np
import math

# Function that calculates the gps coordinates of a point
# given the edn coordinates of the point and the gps
# coordinates of the origin of the edn coordinate system

# Note that all input/output should be in degrees
def gps_from_edn(enu_origin, edn):

    a = 6378137 # Equatorial radius of the earth [m]
    e2 = 0.00669437999 # e = eccentricity of the ellipsoid
    b = a * math.sqrt(1 - e2)

    lat_o = enu_origin[0, 0]
    long_o = enu_origin[1, 0]
    alt_o = enu_origin[2, 0]

    lat_sin = math.sin(math.pi * lat_o / 180)
    lat_cos = math.cos(math.pi * lat_o / 180)
    long_sin = math.sin(math.pi * long_o / 180)
    long_cos = math.cos(math.pi * long_o / 180)

    # Calculate the prime vertical radius of curvature at the given latitude
    N = a / math.sqrt(1 - e2 * math.pow(lat_sin, 2))

    # Calculate the ECEF coordinates of the EDN origin
    X_o = (N + alt_o) * lat_cos * long_cos
    Y_o = (N + alt_o) * lat_cos * long_sin
    Z_o = (math.pow(b, 2) / math.pow(a, 2) * N + alt_o) * lat_sin
    ecef_o = np.array([[X_o], [Y_o], [Z_o]])

    # Calculate rotation matrices for coordinate transformation
    R = np.array([[-long_sin, -lat_sin * long_cos, lat_cos * long_cos],
                  [long_cos, -lat_sin * long_sin, lat_cos * long_sin],
                  [0, lat_cos, lat_sin]])

    R_enu = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])

    # Convert from EDN to ENU
    enu = np.matmul(R_enu, edn)

    # Convert from ENU to ECEF
    ecef = np.matmul(R, enu) + ecef_o

    # Calculate some help variables
    ep = e2 / (1 - e2)
    p = math.sqrt(math.pow(ecef[0, 0], 2) + math.pow(ecef[1, 0], 2))
    th = math.atan2(a * ecef[2, 0], b * p)

    # Convert from ECEF to gps
    lon = math.atan2(ecef[1, 0], ecef[0, 0])
    lat = math.atan2((ecef[2, 0] + ep * b * math.pow(math.sin(th), 3)),
                     (p - e2 * a * math.pow(math.cos(th), 3)))
    v = a / math.sqrt(1 - e2 * math.pow(math.sin(lat), 2))
    alt = p / math.cos(lat) - v

    # Convert from radians to degrees
    lon = lon * 180 / math.pi
    lat = lat * 180 / math.pi

    return np.array([[lat], [lon], [alt]])

# Function that transforms the camera coordinates to EDN coordinates
# The input angle should indicate how camera1 points
# NORTH = 0, WEST = pi/2, SOUTH = pi, EAST = -pi/2
def edn_from_camera(camera_coords, angle):
    cos = math.cos(-angle)
    sin = math.sin(-angle)
    R = np.array([[cos, 0, sin], [0, 1, 0], [-sin, 0, cos]])

    return np.matmul(R, camera_coords)
    
gps_from_edn(np.array([[55], [5], [200]]), np.array([[0], [-100], [0]]))    
