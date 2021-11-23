#Haversine Distance function used to compute radius
from math import radians, sin, cos, asin, sqrt, ceil
import pandas as pd
import numpy as np


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Compute distance between two pairs of coordinates (lon1, lat1, lon2, lat2)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 2 * 6371 * asin(sqrt(a))


#Divide Paris into subzones to request more restaurants from Yelp API



def subzones_paris(n_subzones):
    """
    Divide Paris into n_subzones squares. Returns list of centers (lat,lon)
    and the radius (in meters) to use for the API request
    """
    #lat-lon boundaries for Paris
    up_left = np.array([48.9002, 2.2617])
    up_right = np.array([48.9002, 2.4488])
    down_right = np.array([48.8202, 2.4488])
    down_left = np.array([48.8202, 2.2617])

    coor = np.array([up_left, up_right, down_right, down_left])

    #compute distance
    dist_h = up_right - up_left
    dist_v = up_left - down_left

    #divide in n_subzones

    epsilon_h = dist_h / n_subzones**0.5
    epsilon_v = dist_v / n_subzones**0.5

    centers = []
    start = up_left

    for i in range(int(n_subzones**0.5)):
        for j in range(int(n_subzones**0.5)):
            start = (i + 0.5) * epsilon_v + (j + 0.5) * epsilon_h + up_left
            centers.append(start)

    radius = haversine_distance(up_left[0], up_left[1], centers[0][0],
                                centers[0][1])

    return centers, radius * 1000
