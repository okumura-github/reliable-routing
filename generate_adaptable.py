import random as rnd
import math
import sys
import numpy
import pickle

from link import Link
from traffic import Traffic
from define import Define

def write_log(msg, file_name):
    try:
        f = open(file_name, 'a')
        f.write(msg)
        f.write("\n")
        f.close()
    except IOError as e:
        print('except: Cannot open "{0}"'.format(LOG_FILE), file=sys.stderr)
        print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
        write_log(msg)

def get_bandwidth_rand():
    # i = rnd.randint(0, 3)
    # if i == 0:
    #     return 10
    # elif i == 1:
    #     return 40
    # elif i == 2:
    #     return 80
    # elif i == 3:
    #     return 160
    # else:
    #     return 1
    return rnd.randint(10, 150)


def get_quality_rand():
    return 1.1


def get_nodes_rand(p_node_size):
    start_node = rnd.randint(1, p_node_size)
    while True:
        end_node = rnd.randint(1, p_node_size)
        if start_node != end_node:
            break
    return [start_node, end_node]
    # return [1, 7]


def get_failure_rate_rand():
    i = rnd.randint(0, 2)
    if i == 0:
        return 0.01
    if i == 1:
        return 0.03
    if i == 2:
        return 0.05
    else:
        return 0.01


def get_shape():
    return 2


def get_scale_rand():    #何か月で一回壊れるか/何か月で全リンク故障する
    # i = rnd.randint(0, 2)
    # if i == 0:
    #     return 100
    # if i == 1:
    #     return 33
    # if i == 2:
    #     return 20
    # else:
    #     return 100
    return 37


def get_initial_age():
    i = rnd.randint(0, 2)
    if i == 0:
        return 0
    if i == 1:
        return 1
    if i == 2:
        return 2
    else:
        return 1


def load_topology(p_file_path, p_link_list):
    f = open(p_file_path, 'r')
    line = f.readline()  # 1行を文字列として読み込む(改行文字も含まれる)
    node_count = int(line)
    # ノード集合
    nodes = range(1, node_count + 1)
    line = f.readline()

    while line:
        data = line[:-1].split(' ')
        if len(data) == 3 and data[0].isdigit() and data[1].isdigit() and data[2].isdigit():
            p_link_list[(int(data[0]), int(data[1]))] = Link(distance=int(data[2]), bandwidth=1000,
                                                             failure_rate=0,
                                                             shape=10,
                                                             scale=30,
                                                             age=get_initial_age())
        line = f.readline()
    f.close()
    return (node_count, p_link_list)

########### variables ###########
TOPOLOGY_FILE = 'topology_nsfnet.txt'
HOLDING_TIME = 5  # 平均トラフィック保持時間
TOTAL_TRAFFIC = 1000  # 総トラフィック量 1000
MAX_ROUTE = 5# 一つの要求に使用される最大ルート数
AVERAGE_REPAIRED_TIME = 1
##注意！shape, scaleなど反映させたいときはload_topology内を変更させないと！
SHAPE = 10
SCALE = 30


#################################


argv = sys.argv

# トポロジー読み込み
node_size = 0
link_list = {}
(node_size, link_list) = load_topology(TOPOLOGY_FILE, link_list)

for key, item in link_list.items():
    print(key)

# 初期設定生成
# リンク条件生成

if len(argv) > 1:
    print("Traffic per second: %d" % int(argv[1]))

# トラフィック要求発生
TRAFFIC_DEMAND = int(argv[1])  # 一秒当たりの平均トラフィック発生量

define = Define(TRAFFIC_DEMAND, HOLDING_TIME, TOTAL_TRAFFIC, MAX_ROUTE, AVERAGE_REPAIRED_TIME, node_size, SHAPE, SCALE)

traffic_list = []
traffic_count = 0
second = 0

while True:
    traffic_per_second = numpy.random.poisson(TRAFFIC_DEMAND)
    traffic_list.append([])
    # write_log("Second: {}".format(second), LOG_TRAFFIC)
    for num in range(0, traffic_per_second - 1):
        nodes = get_nodes_rand(node_size)
        traffic_list[second].append(Traffic(
            traffic_count, #id
            nodes[0], #start node
            nodes[1], #end node
            round(numpy.random.exponential(HOLDING_TIME - 1)) + 1, #holding time
            # rnd.randint(5, 10),
            get_bandwidth_rand(), #bandwidth
            get_quality_rand())) #quality
        traffic_count += 1
        if traffic_count == TOTAL_TRAFFIC:
            break

    second += 1
    if traffic_count >= TOTAL_TRAFFIC:
        break

print("second: %d" % second)

with open('link_list.dat', mode='wb') as f:
    pickle.dump(link_list, f)

with open('traffic_list.dat', mode='wb') as f:
    pickle.dump(traffic_list, f)

with open('define.dat', mode='wb') as f:
    pickle.dump(define, f)
