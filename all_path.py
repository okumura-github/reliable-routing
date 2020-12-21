import random as rnd
import math
import sys
import numpy
import pickle
import copy
import time as tm
import route_calc_variables
import gurobipy as grb
import matplotlib.pyplot as plt

from link import Link
from traffic import Traffic
from traffic import RouteCalcType
from define import Define
from active_traffic import ActiveTraffic
from solution import Solution

with open('link_list.dat', 'rb') as f:
    link_list = pickle.load(f)  # type: dict[tuple[int, int], Link]
    if type(link_list) is not dict:
        print("link_list.dat is invalid.")
        exit(-1)

def dfs(p, q, available_link_list, now_node, node_sequence, path_probability):
    if now_node == q:
        print(node_sequence + [now_node])
        path_probability[tuple(node_sequence + [now_node])] = 1
    else:
        for (ix, jx) in available_link_list:
            if ix == now_node:
                if not jx in node_sequence:
                    dfs(p, q, available_link_list, jx, node_sequence + [now_node], path_probability)
    
            # if len(node_sequence) == 0:
            #     dfs(p, q, available_link_list, jx, node_sequence + [now_node], path_probability)
            # else:
            #     if ix == now_node and jx != node_sequence[-1]:
            #         dfs(p, q, available_link_list, jx, node_sequence + [now_node], path_probability)

p = 1  # 起点
q = 5  # 終点

available_link_list = []
for (i, j), link_item in link_list.items():
    if link_item.failure_status == 0:
        available_link_list.append((i, j))

available_link_list.remove((1,2))
path_probability  = {}  ##dict{(nodes): probability}

dfs(p, q, available_link_list, p, [], path_probability)

print(path_probability)
