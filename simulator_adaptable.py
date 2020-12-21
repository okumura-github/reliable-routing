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

# Define
LOG_FILE = "log_ecgr.txt"
LOG_FILE2 = "log_mincost.txt"
LOG_FILE3 = "log_dpp.txt"
LOG_FILE4 = "log_kshortest.txt"
LOG_FILE5 = "log_mpp50%.txt"
LOG_FILE6 = "log_mpp40%.txt"
RESULT_FILE = "result.txt"

def write_log(msg):
    try:
        f = open(LOG_FILE, 'a')
        f.write(msg)
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log(msg)


def write_log2(msg):
    # return
    try:
        f = open(LOG_FILE2, 'a')
        f.write(msg)
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE2), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log2(msg)


def write_log3(msg):
    # return
    try:
        f = open(LOG_FILE3, 'a')
        f.write(msg)
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE3), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log3(msg)


def write_log4(msg):
    # return
    try:
        f = open(LOG_FILE4, 'a')
        f.write(msg)
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE4), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log4(msg)

def write_log5(msg):
    # return
    try:
        f = open(LOG_FILE5, 'a')
        f.write(msg)
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE5), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log5(msg)

def write_log6(msg):
    # return
    try:
        f = open(LOG_FILE6, 'a')
        f.write(msg)
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE6), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log6(msg)

def show_links(p_link_list):
    """

    :param p_link_list:
    :type p_link_list: dict[(int, int),Link]
    """
    bandwidth_str = ""
    for key, link in p_link_list.items():
        if type(link) == Link and link.failure_status == 0:
            bandwidth_str += "%d %d %d\n" % (key[0], key[1], link.bandwidth)

    return bandwidth_str


def show_links_wR(p_link_list, holding_time):
    """

    :param holding_time:
    :type holding_time: int
    :param p_link_list:
    :type p_link_list: dict[(int, int),Link]
    """
    bandwidth_str = ""
    for key, link in p_link_list.items():
        if type(link) == Link and link.failure_status == 0:
            bandwidth_str += "%d %d %d %f\n" % (
                key[0], key[1], link.bandwidth, link.calculate_reliability(holding_time))

    return bandwidth_str


start_time = tm.time()

# ファイルからオブジェクト読み込み
with open('define.dat', 'rb') as f:
    define = pickle.load(f)  # type: Define
    if type(define) is not Define:
        print("define.dat is invalid.")
        exit(-1)

with open('link_list.dat', 'rb') as f:
    link_list = pickle.load(f)  # type: dict[tuple[int, int], Link]
    if type(link_list) is not dict:
        print("link_list.dat is invalid.")
        exit(-1)

with open('traffic_list.dat', 'rb') as f:
    traffic_list = pickle.load(f)  # type: list[list[Traffic]]
    if type(traffic_list) is not list:
        print("traffic_list.dat is invalid.")
        exit(-1)

with open('fail_repair.dat', 'rb') as f:
    fail_repair_list = pickle.load(f)
    if type(fail_repair_list) is not list:
        print("fail_repair.dat is invalid.")
        exit(-1)

TOTAL_TRAFFIC = define.total_traffic
MAX_ROUTE = define.max_route
AVERAGE_REPAIRED_TIME = define.avg_repaired_time

total_requested_bandwidth = 0
for traffic_sec_list in traffic_list:
    for traffic_item in traffic_sec_list:  # type: Traffic
        total_requested_bandwidth += traffic_item.bandwidth

print("total requested bandwidth: {}".format(total_requested_bandwidth))

active_traffic_list = []  # type: list[ActiveTraffic]
active_traffic_list2 = []  # type: list[ActiveTraffic]
active_traffic_list3 = []  # type: list[ActiveTraffic]
active_traffic_list4 = []  # type: list[ActiveTraffic]
active_traffic_list5 = []
active_traffic_list6 = []
current_link_list = copy.deepcopy(link_list) #ecgr
current_link_list2 = copy.deepcopy(link_list) #mincost
current_link_list3 = copy.deepcopy(link_list) #dpp
current_link_list4 = copy.deepcopy(link_list) #adaptive ecgr
current_link_list5 = copy.deepcopy(link_list) #mpp 50*3
current_link_list6 = copy.deepcopy(link_list) #mpp 40*3


node_size = define.node_size

time = 0
blocked_bandwidth = 0
blocked_demand = 0
request_achieved_demand = 0
total_expected_bandwidth = 0
total_requested_expected_bandwidth = 0
blocked_bandwidth2 = 0
blocked_demand2 = 0
request_achieved_demand2 = 0
total_expected_bandwidth2 = 0
total_requested_expected_bandwidth2 = 0
blocked_bandwidth3 = 0
blocked_demand3 = 0
request_achieved_demand3 = 0
total_expected_bandwidth3 = 0
total_requested_expected_bandwidth3 = 0
blocked_bandwidth4 = 0
blocked_demand4 = 0
request_achieved_demand4 = 0
total_expected_bandwidth4 = 0
total_requested_expected_bandwidth4 = 0
blocked_bandwidth5 = 0
blocked_demand5 = 0
request_achieved_demand5 = 0
total_expected_bandwidth5 = 0
total_requested_expected_bandwidth5 = 0
blocked_bandwidth6 = 0
blocked_demand6 = 0
request_achieved_demand6 = 0
total_expected_bandwidth6 = 0
total_requested_expected_bandwidth6 = 0

total_data_achieved_demand = 0
total_data_achieved_demand2 = 0
total_data_achieved_demand3 = 0
total_data_achieved_demand4 = 0
total_data_achieved_demand5 = 0
total_data_achieved_demand6 = 0

total_data_requested = 0
total_data_requested2 = 0
total_data_requested3 = 0
total_data_requested4 = 0
total_data_requested5 = 0
total_data_requested6 = 0

total_data_transmitted = 0
total_data_transmitted2 = 0
total_data_transmitted3 = 0
total_data_transmitted4 = 0
total_data_transmitted5 = 0
total_data_transmitted6 = 0

request_accept = {}
request_block = {}

success_x = []
success_y = []
block_x = []
block_y = []

while True:
    write_log("\nSimulation Time: %d\n" % time)
    write_log2("\nSimulation Time: %d\n" % time)
    write_log3("\nSimulation Time: %d\n" % time)
    write_log4("\nSimulation Time: %d\n" % time)
    write_log5("\nSimulation Time: %d\n" % time)
    write_log6("\nSimulation Time: %d\n" % time)

    # リンク障害判定
    # Link.process_link_status(current_link_list, current_link_list2, current_link_list3, current_link_list4,
    #                          active_traffic_list, active_traffic_list2, active_traffic_list3, active_traffic_list4,
    #                          AVERAGE_REPAIRED_TIME)
    Link.new_process_link_status(current_link_list, current_link_list2, current_link_list3, current_link_list4, current_link_list5, current_link_list6,
                             active_traffic_list, active_traffic_list2, active_traffic_list3, active_traffic_list4, active_traffic_list5, active_traffic_list6,
                             fail_repair_list[time], time)

    ###################### OkumuraECGR開始 ######################
    # 使用可能容量加算
    for active_traffic_item in active_traffic_list[:]:
        expected_bandwidth = active_traffic_item.traffic.bandwidth * active_traffic_item.traffic.quality  # 帯域幅期待値
        total_bandwidth = 0
        
        for route in active_traffic_item.routes[:]:
            count_flag = False
            for route_link_key, route_link_item in route.items():
                if current_link_list[route_link_key].failure_status == 1:
                    count_flag = True  ##ルートに含まれるリンクのうちひとつでも故障していたらTrueにする
                # total_bandwidth += route_link_item.bandwidth
                # break
            if count_flag == False:
                for route_link_key, route_link_item in route.items():
                    total_bandwidth += route_link_item.bandwidth
                    break
        active_traffic_item.traffic.total_data += total_bandwidth
        write_log("[Total Data(%d)] %d->%d %d\n" % (
            active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
            active_traffic_item.traffic.end_node, active_traffic_item.traffic.total_data))
        

    for active_traffic in active_traffic_list[:]:
        if active_traffic.end_time <= time:
            # 回線使用終了
            ## ここはECGRでもactive_traffic.traffic.bandwidth * 1でよいはず
            expected_bandwidth = active_traffic.traffic.bandwidth * active_traffic.traffic.quality
            # expected_bandwidth = active_traffic.traffic.bandwidth * active_traffic.traffic.quality
            total_bandwidth = 0
            for route in active_traffic.routes:
                added_total_bandwidth = False
                for used_link_key, used_link_item in route.items():
                    if not added_total_bandwidth:
                        total_bandwidth += used_link_item.bandwidth
                        added_total_bandwidth = True
                    current_link_list[(used_link_key[0], used_link_key[1])].bandwidth += used_link_item.bandwidth
                    write_log("Link %d->%d add bandwidth: %d\n" % (
                        used_link_key[0], used_link_key[1], used_link_item.bandwidth))

            if total_bandwidth >= expected_bandwidth:
                request_achieved_demand += 1
                write_log("[End(%d)] %d->%d (%d, %f), %d\n" % (
                    active_traffic.traffic.id, active_traffic.traffic.start_node, active_traffic.traffic.end_node,
                    active_traffic.traffic.bandwidth, active_traffic.traffic.quality, active_traffic.end_time))
            else:
                write_log("total: {}, expected: {}\n".format(total_bandwidth, expected_bandwidth))
                write_log("[End with Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d, %d\n" % (
                    active_traffic.traffic.id, active_traffic.traffic.start_node, active_traffic.traffic.end_node,
                    active_traffic.traffic.bandwidth, active_traffic.traffic.quality, total_bandwidth,
                    active_traffic.end_time))

            ## ECGRでもTCARを求めるときはqualityかけなくていいはず
            # if active_traffic.traffic.total_data >= active_traffic.traffic.bandwidth * active_traffic.traffic.quality * active_traffic.actual_holding_time:
            if active_traffic.traffic.total_data >= active_traffic.traffic.bandwidth * 1 * active_traffic.actual_holding_time:
                total_data_achieved_demand += 1
                write_log("[Achieve Total Data Success(%d)] %d->%d, total transfer data: %d, request data: %d\n" % (
                    active_traffic.traffic.id, active_traffic.traffic.start_node, active_traffic.traffic.end_node,
                    active_traffic.traffic.total_data, active_traffic.traffic.bandwidth * 1 * active_traffic.actual_holding_time
                    ))
            else:
                # write_log("[Achieve Total Data Failed(%d)] %d->%d (%d, %f, %d) %d\n" % (
                #     active_traffic.traffic.id, active_traffic.traffic.start_node, active_traffic.traffic.end_node,
                #     active_traffic.traffic.bandwidth, active_traffic.traffic.quality,
                #     active_traffic.traffic.holding_time,
                #     total_bandwidth))
                write_log("[Achieve Total Data Failed(%d)] %d->%d, total transfer data: %d, request data: %d\n" % (
                    active_traffic.traffic.id, active_traffic.traffic.start_node, active_traffic.traffic.end_node,
                    active_traffic.traffic.total_data, active_traffic.traffic.bandwidth * 1 * active_traffic.actual_holding_time
                    ))
            total_data_transmitted += active_traffic.traffic.total_data
            active_traffic_list.remove(active_traffic)
    write_log(show_links(current_link_list))
    if len(traffic_list) > 0:
        for traffic_item in traffic_list[0]:
            if traffic_item.id % (TOTAL_TRAFFIC / 100) == 0:
                print(traffic_item.id)

            model_list = {}
            variable_list = {}
            solution = Solution()
            current_available_link_list = []  # type: list[tuple[int, int]]
            K = range(1, MAX_ROUTE + 1)

            # ルート計算
            actual_holding_time = traffic_item.CalcRoute(solution, RouteCalcType.OkumuraECGR, MAX_ROUTE,
                                                         node_size, current_link_list, current_available_link_list)
            if not actual_holding_time:
                print("Undefined route calculation type\n")
                exit(-1)
            
            print("solution.status: {}".format(solution.status))
            # solution.status = grb.GRB.OPTIMAL

            # for key, item in solution.variables["b"].items():
            #     print(key,item)
            # exit(-1)
            if solution.status == grb.GRB.OPTIMAL:
                routes = [{} for i in range(MAX_ROUTE)]  # type: list[dict[tuple[int, int], Link]]
                for k in K:
                    if solution.variables["b"][k] != 0:
                        for (i, j) in current_available_link_list:
                            if solution.variables["y"][(k, i, j)] != 0:
                                routes[k - 1][(i, j)] = Link(current_link_list[(i, j)].distance,
                                                             solution.variables["y"][(k, i, j)],
                                                             current_link_list[(i, j)].failure_rate, 0, define.shape,
                                                             define.scale)
                total_requested_expected_bandwidth += traffic_item.bandwidth * traffic_item.quality
                total_data_requested += traffic_item.bandwidth * traffic_item.quality * traffic_item.holding_time
                write_log("[Accepted(%d)] %d->%d (%d, %f) for %d  \n" % (
                    traffic_item.id, traffic_item.start_node, traffic_item.end_node,
                    traffic_item.bandwidth * traffic_item.holding_time,
                    traffic_item.quality, actual_holding_time))
                success_x.append(traffic_item.holding_time)
                success_y.append(traffic_item.bandwidth)

                # ルート使用処理
                route_cnt = 0
                active_traffic = ActiveTraffic(time + actual_holding_time, actual_holding_time, copy.copy(traffic_item),
                                               [])
                for route in routes:
                    route_reliability = 1
                    if len(route) > 0:
                        route_cnt += 1
                        route_bandwidth = 0
                        for (i, j), link in route.items():
                            route_bandwidth = link.bandwidth
                            current_link_list[(i, j)].bandwidth -= link.bandwidth
                            route_reliability *= current_link_list[(i, j)].calculate_reliability(
                                actual_holding_time)
                            write_log("Link %d->%d remove bandwidth: %d\n" % (i, j, link.bandwidth))
                        active_traffic.routes.append(route)
                        total_expected_bandwidth += route_reliability * route_bandwidth
                active_traffic_list.append(active_traffic)

                if actual_holding_time in request_accept:
                    request_accept[actual_holding_time] = request_accept[actual_holding_time] + 1
                else:
                    request_accept[actual_holding_time] = 1

            else:
                # 最適解なし
                # print("Blocked")
                write_log(show_links_wR(current_link_list, actual_holding_time))
                write_log("[Blocked(%d)] %d->%d (%d, %f)\n" % (
                    traffic_item.id, traffic_item.start_node, traffic_item.end_node, traffic_item.bandwidth,
                    traffic_item.quality))
                block_x.append(traffic_item.holding_time)
                block_y.append(traffic_item.bandwidth)

                blocked_bandwidth += traffic_item.bandwidth
                blocked_demand += 1

                if actual_holding_time in request_block:
                    request_block[actual_holding_time] = request_block[actual_holding_time] + 1
                else:
                    request_block[actual_holding_time] = 1
            
            # solution.statusを表示
            print("[{}] solution status = {}".format(traffic_item.id, solution.status))
    ###################### ECGR終わり ######################


    print(str(time) + " is done")
    time += 1
    if len(traffic_list) > 0:
        traffic_list.pop(0)

    if (len(traffic_list) == 0 and len(active_traffic_list) == 0 and len(active_traffic_list2) == 0 and len(
            active_traffic_list3) == 0 and len(active_traffic_list4) == 0 and len(active_traffic_list5) == 0 and len(active_traffic_list6) == 0):
        break

write_log(
    "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\n"
    % (blocked_demand, blocked_demand * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth,
       request_achieved_demand,
       ((request_achieved_demand * 100 / (TOTAL_TRAFFIC - blocked_demand)) if (
               TOTAL_TRAFFIC - blocked_demand != 0) else 0),
       total_expected_bandwidth, total_requested_expected_bandwidth))

write_log2(
    "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\n"
    % (blocked_demand2, blocked_demand2 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth2,
       request_achieved_demand2,
       ((request_achieved_demand2 * 100 / (TOTAL_TRAFFIC - blocked_demand2)) if (
               TOTAL_TRAFFIC - blocked_demand2 != 0) else 0),
       total_expected_bandwidth2, total_requested_expected_bandwidth2))

write_log3(
    "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\n"
    % (blocked_demand3, blocked_demand3 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth3,
       request_achieved_demand3,
       ((request_achieved_demand3 * 100 / (TOTAL_TRAFFIC - blocked_demand3)) if (
               TOTAL_TRAFFIC - blocked_demand3 != 0) else 0),
       total_expected_bandwidth3, total_requested_expected_bandwidth3))

# write_log4(
#     "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\n"
#     % (blocked_demand4, blocked_demand4 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth4,
#        request_achieved_demand4,
#        ((request_achieved_demand4 * 100 / (TOTAL_TRAFFIC - blocked_demand4)) if (
#                TOTAL_TRAFFIC - blocked_demand4 != 0) else 0),
#        total_expected_bandwidth4, total_requested_expected_bandwidth4))

write_log5(
    "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\n"
    % (blocked_demand5, blocked_demand5 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth4,
       request_achieved_demand5,
       ((request_achieved_demand5 * 100 / (TOTAL_TRAFFIC - blocked_demand5)) if (
               TOTAL_TRAFFIC - blocked_demand5 != 0) else 0),
       total_expected_bandwidth5, total_requested_expected_bandwidth5))

# write_log6(
#     "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\n"
#     % (blocked_demand6, blocked_demand6 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth4,
#        request_achieved_demand6,
#        ((request_achieved_demand6 * 100 / (TOTAL_TRAFFIC - blocked_demand6)) if (
#                TOTAL_TRAFFIC - blocked_demand6 != 0) else 0),
#        total_expected_bandwidth6, total_requested_expected_bandwidth6))

with open(RESULT_FILE, "a") as f:
    f.write("\n")
    f.write(
        "Condition: Traffic demand: %d, Holding time: %d, Total traffic: %d, Max route: %d, Avg repair time: %d Shape: %d, Scale: %d\n"
        % (define.traffic_demand, define.holding_time, define.total_traffic, define.max_route,
           define.avg_repaired_time, define.shape, define.scale))
    f.write("Propose\n")
    f.write(
        "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d(%d%%)\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\nTotal data achieved demand: %d\nTotal data transmitted: %d\nTotal data requested: %d\nTCAR: %d%%\n"
        % (blocked_demand, blocked_demand * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth,
           blocked_bandwidth / total_requested_bandwidth * 100,
           request_achieved_demand,
           ((request_achieved_demand * 100 / (TOTAL_TRAFFIC - blocked_demand)) if (
                   TOTAL_TRAFFIC - blocked_demand != 0) else 0),
           total_expected_bandwidth, total_requested_expected_bandwidth, total_data_achieved_demand,
           total_data_transmitted, total_data_requested,
           ((total_data_achieved_demand * 100 / (TOTAL_TRAFFIC - blocked_demand)) if (
                   TOTAL_TRAFFIC - blocked_demand != 0) else 0)))
    f.write("MinCostFlow\n")
    f.write(
        "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d(%d%%)\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\nTotal data achieved demand: %d\nTotal data transmitted: %d\nTotal data requested: %d\nTCAR: %d%%\n"
        % (blocked_demand2, blocked_demand2 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth2,
           blocked_bandwidth2 / total_requested_bandwidth * 100,
           request_achieved_demand2,
           ((request_achieved_demand2 * 100 / (TOTAL_TRAFFIC - blocked_demand2)) if (
                   TOTAL_TRAFFIC - blocked_demand2 != 0) else 0),
           total_expected_bandwidth2, total_requested_expected_bandwidth2, total_data_achieved_demand2,
           total_data_transmitted2, total_data_requested2,
           ((total_data_achieved_demand2 * 100 / (TOTAL_TRAFFIC - blocked_demand2)) if (
                   TOTAL_TRAFFIC - blocked_demand2 != 0) else 0)))
    f.write("Backup\n")
    f.write(
        "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d(%d%%)\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\nTotal data achieved demand: %d\nTotal data transmitted: %d\nTotal data requested: %d\nTCAR: %d%%\n"
        % (blocked_demand3, blocked_demand3 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth3,
           blocked_bandwidth3 / total_requested_bandwidth * 100,
           request_achieved_demand3,
           ((request_achieved_demand3 * 100 / (TOTAL_TRAFFIC - blocked_demand3)) if (
                   TOTAL_TRAFFIC - blocked_demand3 != 0) else 0),
           total_expected_bandwidth3, total_requested_expected_bandwidth3, total_data_achieved_demand3,
           total_data_transmitted3, total_data_requested3,
           ((total_data_achieved_demand3 * 100 / (TOTAL_TRAFFIC - blocked_demand3)) if (
                   TOTAL_TRAFFIC - blocked_demand3 != 0) else 0)))
    f.write("K-shortest ECGR\n")
    f.write(
        "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d(%d%%)\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\nTotal data achieved demand: %d\nTotal data transmitted: %d\nTotal data requested: %d\nTCAR: %d%%\n"
        % (blocked_demand4, blocked_demand4 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth4,
           blocked_bandwidth4 / total_requested_bandwidth * 100,
           request_achieved_demand4,
           ((request_achieved_demand4 * 100 / (TOTAL_TRAFFIC - blocked_demand4)) if (
                   TOTAL_TRAFFIC - blocked_demand4 != 0) else 0),
           total_expected_bandwidth4, total_requested_expected_bandwidth4, total_data_achieved_demand4,
           total_data_transmitted4, total_data_requested4,
           ((total_data_achieved_demand4 * 100 / (TOTAL_TRAFFIC - blocked_demand4)) if (
                   TOTAL_TRAFFIC - blocked_demand4 != 0) else 0)))
    f.write("Multipath Provisioning 50% 3path\n")
    f.write(
        "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d(%d%%)\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\nTotal data achieved demand: %d\nTotal data transmitted: %d\nTotal data requested: %d\nTCAR: %d%%\n"
        % (blocked_demand5, blocked_demand5 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth5,
           blocked_bandwidth5 / total_requested_bandwidth * 100,
           request_achieved_demand5,
           ((request_achieved_demand5 * 100 / (TOTAL_TRAFFIC - blocked_demand5)) if (
                   TOTAL_TRAFFIC - blocked_demand5 != 0) else 0),
           total_expected_bandwidth5, total_requested_expected_bandwidth5, total_data_achieved_demand5,
           total_data_transmitted5, total_data_requested5,
           ((total_data_achieved_demand5 * 100 / (TOTAL_TRAFFIC - blocked_demand5)) if (
                   TOTAL_TRAFFIC - blocked_demand5 != 0) else 0)))
    f.write("Multipath Provisioning 40% 3path\n")
    f.write(
        "Blocked demand:%d(%d%%)\nTotal bandwidth: %d\nBlocked bandwidth: %d(%d%%)\nBandwidth achieved demand: %d(%d%%)\nTotal expected bandwidth: %d\nTotal requested expected bandwidth: %d\nTotal data achieved demand: %d\nTotal data transmitted: %d\nTotal data requested: %d\nTCAR: %d%%\n"
        % (blocked_demand6, blocked_demand6 * 100 / TOTAL_TRAFFIC, total_requested_bandwidth, blocked_bandwidth6,
           blocked_bandwidth6 / total_requested_bandwidth * 100,
           request_achieved_demand6,
           ((request_achieved_demand6 * 100 / (TOTAL_TRAFFIC - blocked_demand6)) if (
                   TOTAL_TRAFFIC - blocked_demand6 != 0) else 0),
           total_expected_bandwidth6, total_requested_expected_bandwidth6, total_data_achieved_demand6,
           total_data_transmitted6, total_data_requested6,
           ((total_data_achieved_demand6 * 100 / (TOTAL_TRAFFIC - blocked_demand6)) if (
                   TOTAL_TRAFFIC - blocked_demand6 != 0) else 0)))
    f.write("\n")
    f.write("success holding time\n")
    for key, item in request_accept.items():
        f.write("holding time: {}, count: {}\n".format(key, item))

    f.write("\n")
    f.write("block holding time\n")
    for key, item in request_block.items():
        f.write("holding time: {}, count: {}\n".format(key, item))

end_time = tm.time()

print('Elapsed Time: %f' % (end_time - start_time))

plt.scatter(success_x, success_y, label='success', color='blue')
plt.scatter(block_x, block_y, label='block', color='red')
plt.xlabel('holding time')
plt.ylabel('capacity / unit time')
plt.legend()
plt.savefig('figure.png')
