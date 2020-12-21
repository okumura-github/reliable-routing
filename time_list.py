import random as rnd
import math
import sys
import numpy
import pickle
import copy
import time as tm
import route_calc_variables
import gurobipy as grb

from link import Link
from traffic import Traffic
from traffic import RouteCalcType
from define import Define
from active_traffic import ActiveTraffic
from solution import Solution


with open('traffic_list.dat', 'rb') as f:
    traffic_list = pickle.load(f)  # type: list[list[Traffic]]
    if type(traffic_list) is not list:
        print("traffic_list.dat is invalid.")
        exit(-1)

time_count = {}
for traffic_second in traffic_list:
    for traffic in traffic_second:
        if traffic.holding_time in time_count.keys():
            time_count[traffic.holding_time] += 1
        else:
            time_count[traffic.holding_time] = 1

print(time_count)