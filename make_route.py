import pickle
import math
from link import Link
from route_calc_variables import RouteCalcVariables
from solution import Solution

with open('fail_repair.dat', 'rb') as f:
    fail_repair_list = pickle.load(f)
    if type(fail_repair_list) is not list:
        print("fail_repair.dat is invalid.")
        exit(-1)
        
def calc_path_reliability(nodes, link_info, holding_time):
    reliable_probability = 1.0
    for i in range(len(nodes) -1):
        reliable_probability = reliable_probability * link_info[(nodes[i], nodes[i + 1])].calculate_reliability(holding_time)
    return reliable_probability

available_link_list = []
for i in range(5):
    for j in range(5):
        if i != j:
            available_link_list.append((i + 1, j + 1))

## test
# available_link_list.remove((2, 1))
# available_link_list.remove((2, 5))
# available_link_list.remove((5, 2))
# # available_link_list.remove((5, 4))
# available_link_list.remove((4, 1))
# available_link_list.remove((4, 2))
# available_link_list.remove((4, 5))
# available_link_list.remove((1, 3))
# available_link_list.remove((1, 4))
# fail_repair_list[0][(1, 2)].bandwidth = 80
# fail_repair_list[0][(2, 3)].bandwidth = 50
# fail_repair_list[0][(2, 4)].bandwidth = 50
# fail_repair_list[0][(1, 5)].bandwidth = 200
# fail_repair_list[0][(5, 3)].bandwidth = 100
# fail_repair_list[0][(5, 4)].bandwidth = 200
# fail_repair_list[0][(4, 3)].bandwidth = 200
fail_repair_list[0][(5, 3)].failure_status = 1
available_link_list.remove((5, 3))

print("node 1 -> node 3")

print("availble link")
print(available_link_list)

for link_info in fail_repair_list:
    src = 1
    dst = 3
    path_probability = {}
    for (i1, j1) in available_link_list:
        if i1 == src:
            node1 = i1
            if j1 == dst:
                node2 = j1
                # route_list.append((node1, node2))
                path_probability[(node1, node2)] = calc_path_reliability((node1, node2), link_info, 10)
                # print(node1, node2)
            else:
                node2 = j1
                for (i2, j2) in available_link_list:
                    if i2 == j1 and j2 != node1 and j2 != node2:
                        if j2 == dst:
                            node3 = j2
                            # route_list.append((node1, node2, node3))
                            path_probability[(node1, node2, node3)] = calc_path_reliability((node1, node2, node3), link_info, 10)
                            # print(node1, node2, node3)
                        else:
                            node3 = j2
                            for (i3, j3) in available_link_list:
                                if i3 == j2 and j3 != node1 and j3 !=node2 and j3 != node3:
                                    if j3 == dst:
                                        node4 = j3
                                        # route_list.append((node1, node2, node3, node4))
                                        path_probability[(node1, node2, node3, node4)] = calc_path_reliability((node1, node2, node3, node4), link_info, 10)
                                        # print(node1, node2, node3, node4)
                                    else:
                                        node4 = j3
                                        print("for")
                                        for (i4, j4) in available_link_list:
                                            print(i4, j4)
                                            if i4 == j3 and j4 != node1 and j4 != node2 and j4 != node3 and j4 != node4:
                                                if j4 == dst:
                                                    node5 = j4
                                                    # route_list.append((node1, node2, node3, node4, node5))
                                                    path_probability[(node1, node2, node3, node4, node5)] = calc_path_reliability((node1, node2, node3, node4, node5), link_info, 10)
                                                    # print(node1, node2, node3, node4, node5)
                                                else:
                                                    print("error")
    break

for key, item in path_probability.items():
    print("{}: path_reliability {}".format(key, item))

exit(-1)

max_key = max(path_probability, key = path_probability.get)
print(max_key)

link_info = fail_repair_list[0]
K = range(1, 5 + 1)
# print(link_info[(1, 2)].bandwidth)

variables = RouteCalcVariables()
for (i, j), link_item in link_info.items():
    if link_item.failure_status == 0:
        for k in K:
            variables.x[k, i, j] = 0
            variables.y[k, i, j] = 0

for k in K:
    variables.b[k] = 0

required_capacity = 200
quality = 1.1
remain_capacity = required_capacity * quality
expected_capacity = 0
actual_capacity = 0
path_capacity_limit = 0.5
holding_time = 5

# link_info[(2, 3)].bandwidth = 300
# link_info[(5, 2)].bandwidth = 100

# ## test
# link_info[(2, 1)].failure_status = 1
# link_info[(2, 5)].failure_status = 1
# link_info[(5, 2)].failure_status = 1
# link_info[(5, 4)].failure_status = 1
# link_info[(4, 1)].failure_status = 1
# link_info[(4, 2)].failure_status = 1
# link_info[(4, 5)].failure_status = 1
# link_info[(1, 3)].failure_status = 1
# link_info[(1, 4)].failure_status = 1


# while(len(path_probability)):
for number in range(len(path_probability)):
    max_key = max(path_probability, key = path_probability.get)

    print("{} {}".format(max_key, path_probability[max_key]))

    ## ここでパス中の最小リンク容量をpath_min_capacityへ代入
    path_min_capacity = 999999
    for i in range(len(max_key) - 1):
        previous = 0
        for k in range(1, number + 1):
            previous += variables.y[k, max_key[i], max_key[i + 1]]
        if path_min_capacity >= link_info[(max_key[i], max_key[i + 1])].bandwidth - previous:
            path_min_capacity = link_info[(max_key[i], max_key[i + 1])].bandwidth - previous

    ## もしpath_min_capacityが１経路あたりの最大容量よりも大きい場合
    reserve_capacity = 0
    if path_min_capacity >= required_capacity * path_capacity_limit:
        reserve_capacity = required_capacity * path_capacity_limit
    else:
        reserve_capacity = path_min_capacity
    
    ## 必要以上に容量を確保しないように調整
    if expected_capacity + reserve_capacity * calc_path_reliability(max_key, link_info, holding_time) > required_capacity * quality:
        reserve_capacity = math.ceil((required_capacity * quality - expected_capacity) / calc_path_reliability(max_key, link_info, holding_time))
    
    ## 容量期待値、実際の容量を加算
    expected_capacity += reserve_capacity * calc_path_reliability(max_key, link_info , holding_time)
    actual_capacity += reserve_capacity
    print("path[{}] current EC = {}, actulal C = {}".format(number + 1, expected_capacity, actual_capacity))

    ## variable x,y,bへ代入
    for j in range(len(max_key) - 1):
        variables.x[number + 1, max_key[j], max_key[j + 1]] = 1
        variables.y[number + 1, max_key[j], max_key[j + 1]] = reserve_capacity
    variables.b[number + 1] = reserve_capacity

    ## 容量期待値が要求容量×Qを超えれば終わり
    if expected_capacity > required_capacity * quality:
        break

    ## 扱った最大信頼確率をもつパスを消去
    del path_probability[max_key]

if expected_capacity < required_capacity * quality:
    print("Blocked !!")
else:
    print("ok")

## x,y,b 確認用
print("x")
for key, item in variables.x.items():
    if item != 0:
        print("x{} : {}".format(key, item))

print("y")
for key, item in variables.y.items():
    if item != 0:
        print("y{} : {}".format(key, item))

print("b")
for key, item in variables.b.items():
    print("b{} : {}".format(key, item))