import numpy as np
import math

def gps_from_edn(enu_origin, edn):

    a = 6378137 # Equatorial radius of the earth [m]
    e2 = 0.00669437999
    b = a * math.sqrt(1 - e2)

    lat_o = enu_origin[0, 0]
    long_o = enu_origin[1, 0]
    alt_o = enu_origin[2, 0]

    lat_sin = math.sin(math.pi * lat_o / 180)
    lat_cos = math.cos(math.pi * lat_o / 180)
    long_sin = math.sin(math.pi * long_o / 180)
    long_cos = math.cos(math.pi * long_o / 180)

    N = a / math.sqrt(1 - e2 * math.pow(lat_sin, 2))

    X_o = (N + alt_o) * lat_cos * long_cos
    Y_o = (N + alt_o) * lat_cos * long_sin
    Z_o = (math.pow(b, 2) / math.pow(a, 2) * N + alt_o) * lat_sin

    ecef_o = np.array([[X_o], [Y_o], [Z_o]])

    print(X_o, Y_o, Z_o)

    R = np.array([[-long_sin, -lat_sin * long_cos, lat_cos * long_cos],
                  [long_cos, -lat_sin * long_sin, lat_cos * long_sin],
                  [0, lat_cos, lat_sin]])

    R_enu = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])

    enu = np.matmul(R_enu, edn)
    ecef = np.matmul(R, enu) + ecef_o

    ep = e2 / (1 - e2)
    p = math.sqrt(math.pow(ecef[0, 0], 2) + math.pow(ecef[1, 0], 2))
    th = math.atan2(a * ecef[2, 0], b * p)

    lon = math.atan2(ecef[1, 0], ecef[0, 0])
    lat = math.atan2((ecef[2, 0] + ep * b * math.pow(math.sin(th), 3)),
                     (p - e2 * a * math.pow(math.cos(th), 3)))

    v = a / math.sqrt(1 - e2 * math.pow(math.sin(lat), 2))
    alt = p / math.cos(lat) - v

    lon = lon * 180 / math.pi
    lat = lat * 180 / math.pi

    print(lon, lat, alt)

    return np.array([[lon], [lat], [alt]])
    
gps_from_edn(np.array([[55], [5], [200]]), np.array([[-189013.869], [4220.171], [-128642.040]]))    
