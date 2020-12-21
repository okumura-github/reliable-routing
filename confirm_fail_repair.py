import random as rnd
import math
import sys
import numpy
import pickle
import copy
import time as tm
import route_calc_variables

from link import Link

with open('fail_repair.dat', 'rb') as f:
    fail_repair_list = pickle.load(f)
    if type(fail_repair_list) is not list:
        print("fail_repair.dat is invalid.")
        exit(-1)

print("length of fail_repair_list: {}".format(len(fail_repair_list)))

for i in fail_repair_list:
    print(i[(4,1)].failure_status)
    
    # for key, items in i.items():
    #     print("node: {}, Link: {}".format(key, items))
