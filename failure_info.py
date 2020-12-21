import math
import random as rnd
import numpy
import sys
import pickle
import copy

from link import Link

# p_link_listがリンク情報をもつ。(node, node) : Link型を要素にもつ辞書型
# p_link_list[(int(data[0]), int(data[1]))] = Link(distance=int(data[2]), bandwidth=1000,failure_rate=0,shape=get_shape(),scale=get_scale_rand(),age=get_initial_age())
# generate時に一緒にsimulation時間分のリンクの情報をあらかじめ持つリストを作ればよい？
# generate時に作ったら平均要求数によってまた変わってしまうので、独立して作成するようにする
# 例）予め1000秒分のリンク情報・故障イベントをつくっておくみたいなかんじ

# このプログラムはtopology毎に実行され、故障イベントを*.datで出力する

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

def get_initial_age():
    # return rnd.randint(0, get_scale_rand())
    # return 0
    i = rnd.randint(0, 20)
    # if i == 0:
    #     return 0
    # if i == 1:
    #     return 1
    # if i == 2:
    #     return 2
    # else:
    #     return 1
    return i

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
    return p_link_list

########### variables ###########
UNIT_TIME = 1000
AVERAGE_REPAIRED_TIME = 1
LOG_FAIL_RECOVER = "log_fail_repair.txt"

##注意！load_topology内のshape, scaleも変えないと！
#################################

argv = sys.argv
try:
    print("loading ... {}".format(argv[1]))
except IndexError as e:
    print("python3 failure_info.py (topology file)!")
TOPOLOGY_FILE = argv[1]

link_info = {}
link_info = load_topology(TOPOLOGY_FILE, link_info)
fail_repair_info = [] # [link_info, link_info, ...]の形

# for key, item in link_info.items():
#     print("{}: {}".format(key, item))


# 変数UNIT_TIME分の故障イベントを用意しておく
for i in range(UNIT_TIME):
    print("TIME {}".format(i))
    write_log("TIME: {}".format(i), LOG_FAIL_RECOVER)
    # print("TIME: {}".format(i))
    Link.link_status(link_info, AVERAGE_REPAIRED_TIME)
    for key, items in link_info.items():
        write_log("node: {}, failure status: {}".format(key, items.failure_status), LOG_FAIL_RECOVER)
        
    fail_repair_info.append(copy.deepcopy(link_info)) # deepcopyにしないと変更される


### ちゃんとlistとして入っているか確認 ###
write_log(" ", LOG_FAIL_RECOVER)
write_log("check", LOG_FAIL_RECOVER)
count = 0
for i in fail_repair_info:
    write_log("UNIT TIME: {}".format(count), LOG_FAIL_RECOVER)
    for key, items in i.items():
        write_log("node: {}, failure status: {}, failure rate: {}".format(key, items.failure_status, items.failure_rate), LOG_FAIL_RECOVER)
    count = count + 1
########################################


with open('fail_repair.dat', mode='wb') as f:
    pickle.dump(fail_repair_info, f)
