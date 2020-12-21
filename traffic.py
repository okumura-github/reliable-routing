import gurobipy as grb
import sys
import math
import copy
from enum import Enum
from route_calc_variables import RouteCalcVariables
from solution import Solution

# def dfs(p, q, available_link_list, now_node, node_sequence, path_probability):
#     if now_node == q:
#         print(node_sequence + [now_node])
#         path_probability[tuple(node_sequence + [now_node])] =self.calc_path_reliability(node_sequence, link_list, self.holding_time)
#     else:
#         for (ix, jx) in available_link_list:
#             if ix == now_node:
#                 if not jx in node_sequence:
#                     dfs(p, q, available_link_list, jx, node_sequence + [now_node], path_probability)


class RouteCalcType(Enum):
    MinCostFlow = 1
    Backup = 2
    ExpectedCapacityGuarantee = 3
    AdaptableExpectedCapacityGuarantee = 4
    KshortestExpectedCapacityGuarantee = 5
    Multipath = 6
    OkumuraECGR = 7


class Traffic:
    COST_FUNCTION_GRANULARITY = 10

    def dijkstra(self, route_list, start_node, end_node):
        if start_node == end_node:
            path = [start_node]
            cost = 0
            return path, cost

        for i in range(500):
            for j in range(500):
                if route_list[i][j] == 0:
                    route_list[i][j] = math.inf
                if i == start_node and j == start_node:
                    route_list[start_node][start_node] = 0
        hairetu = [[math.inf] * 2 for i in range(500)]
        already = [0] * 500
        now = start_node
        min_index = 10000
        already[now] = 1
        hairetu[now][1] = 0
        hairetu[now][0] = now
        while True:
            minn = math.inf
            for i in range(500):
                if i == now:
                    continue
                if route_list[now][i] != math.inf and already[i] != 1:
                    if hairetu[i][1] > hairetu[now][1] + route_list[now][i]:
                        hairetu[i][0] = now
                        hairetu[i][1] = hairetu[now][1] + route_list[now][i]
            for i in range(500):
                if minn > hairetu[i][0] and already[i] == 0:
                    minn = hairetu[i][0]
                    min_index = i
            if minn == math.inf:
                break
            now = min_index
            already[min_index] = 1

        if already[end_node] == 0:
            path = [start_node]
            cost = math.inf
            return path, cost
        else:
            path = []
            tmp = end_node
            cost = hairetu[tmp][1]
            path.insert(0, end_node)
            while tmp != start_node:
                path.insert(0, hairetu[int(tmp)][0])
                tmp = hairetu[tmp][0]
            return path, cost

    def __init__(self, id, start_node, end_node, holding_time=0, bandwidth=0, quality=0):
        self.id = id
        self.start_node = start_node
        self.end_node = end_node
        self.holding_time = holding_time
        self.bandwidth = bandwidth
        self.quality = quality
        self.total_data = 0

    def LinkUsedCostFunc(self, x):
        return 0
        # return pow(x, 2)

    def AdaptiveOptimize(self, solution, link_list, available_link_list, assigned_capacity, t, K, p, q, nodes, quality):
        m = grb.Model()
        variables = RouteCalcVariables()
        m.setParam('OutputFlag', False)
        m.setParam('TimeLimit', 60)
        bandwidth_max = 0
        N = range(0, self.COST_FUNCTION_GRANULARITY + 1)
        link_used_cost = {}
        link_used_cost_threshold = {}

        max_link_length = 0
        for (i, j), link_item in link_list.items():
            if max_link_length < link_item.distance:
                max_link_length = link_item.distance

        for n in N:
            link_used_cost_threshold[n] = n / self.COST_FUNCTION_GRANULARITY
            link_used_cost[n] = max_link_length * assigned_capacity * t * self.LinkUsedCostFunc(link_used_cost_threshold[n])

        # 変数追加
        for (i, j), link_item in link_list.items():
            if link_item.failure_status == 0:
                bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                for k in K:
                    variables.x[k, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="x_{%d,%d,%d}" % (k, i, j))
                    variables.y[k, i, j] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="y_{%d,%d,%d}" % (k, i, j))
                for n in N:
                    variables.z[n, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="z_{%d,%d,%d}" % (n, i, j))
        for k in K:
            variables.b[k] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="b_{%d}" % k)

        # 目的関数を設定し，最小化を行うことを明示する
        m.setObjective(
            grb.quicksum(grb.quicksum(variables.y[k, i, j] * link_list[i, j].distance * t for (i, j) in available_link_list) for k in K)
            + grb.quicksum(grb.quicksum(variables.z[n, i, j] * link_used_cost[n] for n in N) for (i, j) in available_link_list)
            , grb.GRB.MINIMIZE)  # 目的関数
        m.setAttr("ModelSense", grb.GRB.MINIMIZE)

        # 制約追加
        for i in nodes:
            if i == p:
                for k in K:
                    m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list)
                                == 1, name="flow reservation at node %d route %d" % (i, k))
            if i != p and i != q:
                for k in K:
                    m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list)
                                == 0, name="flow reservation at node %d route %d" % (i, k))

        for (i, j) in available_link_list:
            m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= link_list[(i, j)].bandwidth, name="capacity requirement at (%d, %d)" % (i, j))
            # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, assigned_capacity), name="capacity requirement at (%d, %d)" % (i, j))
            m.addConstr(grb.quicksum(variables.z[n, i, j] for n in N) == 1, name="restrict link used cost func for link (%d, %d)" % (i, j))
            if link_list[i, j].bandwidth != 0:
                for n in N:
                    m.addConstr(grb.quicksum(variables.y[k, i, j] for k in K) / link_list[i, j].initial_bandwidth * variables.z[n, i, j] <= link_used_cost_threshold[n],
                                name="link occupation rate for link (%d, %d) at cost %d" % (i, j, n))
        m.addConstr(grb.quicksum(variables.b[k] for k in K) >= assigned_capacity, name="required capacity requirement")
        m.addConstr(grb.quicksum(variables.b[k] for k in K) - grb.quicksum(
            grb.quicksum(
                (1 - link_list[(i, j)].calculate_reliability(t)) * variables.y[k, i, j] for (i, j) in available_link_list) for k in K) >= quality * assigned_capacity,
                    name="expected capacity requirement")

        for k in K:
            for (i, j) in available_link_list:
                m.addConstr(variables.y[k, i, j] >= variables.b[k] + (bandwidth_max * (variables.x[k, i, j] - 1)), name="st1 at (%d, %d) route %d" % (i, j, k))
                m.addConstr(variables.y[k, i, j] <= link_list[(i, j)].bandwidth * variables.x[k, i, j], name="st2 at (%d, %d) route %d" % (i, j, k))
                m.addConstr(variables.y[k, i, j] >= 0, name="st3 at (%d, %d) route %d" % (i, j, k))

        # モデルに制約条件が追加されたことを反映させる
        m.update()
        # print("elapsed_time for modeling %.5f sec" % (stop - start))

        # 最適化を行い，結果を表示させる
        # m.write("mincostflow.lp")  # mincostflow.lp というファイルに定式化されたモデルを出力する
        # m.write("mincostflow_%d.lp" % t)  # mincostflow.lp というファイルに定式化されたモデルを出力する

        m.optimize()
        solution.setValues(m, variables, t)

        return m

    # 範囲確認
    def doCalcRange(self, solution_list, required_total_capacity, link_list, available_link_list, delta, min_val, max_val, min_noval_upper, max_noval_lower, K, p, q, nodes, quality):
        """
             :type solution_list: dict[int, Solution]
             :type required_total_capacity: int
             :type link_list
             :type link_list: dict[tuple[int, int], Link]
             :type available_link_list: list[tuple[int, int]]
             :type delta: int
             :type min_val: int
             :type max_val: int
             :type min_noval_upper: int
             :type max_noval_lower: int
             :return: list[int,int]
             """

        # 範囲最小値
        for t in range(max_noval_lower, min_val, delta):
            if t not in solution_list:
                solution_list[t] = Solution()
                self.AdaptiveOptimize(solution_list[t], link_list, available_link_list, math.ceil(required_total_capacity / t), t, K, p, q, nodes, quality)
            if solution_list[t].isOptimized():
                if t < min_val:
                    min_val = t
                    break
                if t > max_val:
                    max_val = t
            else:
                if max_val < t < min_noval_upper and min_val < t:
                    min_noval_upper = t
                if max_noval_lower < t < min_val and max_val > t:
                    max_noval_lower = t

        # 範囲最大値
        for t in range(max_val, min_noval_upper, delta):
            if t not in solution_list:
                solution_list[t] = Solution()
                self.AdaptiveOptimize(solution_list[t], link_list, available_link_list, math.ceil(required_total_capacity / t), t, K, p, q, nodes, quality)
            if solution_list[t].isOptimized():
                if t > max_val:
                    max_val = t
            else:
                if max_val < t < min_noval_upper and min_val < t:
                    min_noval_upper = t
                    break

        if delta == 1:
            return [min_val, max_val]
        else:
            return self.doCalcRange(solution_list, required_total_capacity, link_list, available_link_list, int(math.ceil(delta / 2)), min_val, max_val, min_noval_upper, max_noval_lower,
                                    K, p, q, nodes, quality)

    def GetObjVal(self, solution_list, link_list, available_link_list, required_total_capacity, t, K, p, q, nodes, quality, minimum_time, maximum_time, direction=0):
        """

        :param solution_list: dict[int, Solution]
        :param link_list:
        :param available_link_list:
        :param required_total_capacity:
        :param t:
        :param K:
        :param p:
        :param q:
        :param nodes:
        :param quality:
        :param minimum_time:
        :param maximum_time:
        :param direction:
        :return:
        """
        assigned_capacity = math.ceil(required_total_capacity / t)
        print("assigned_capacity2: %f" % assigned_capacity)
        if t not in solution_list:
            solution_list[t] = Solution()
            self.AdaptiveOptimize(solution_list[t], link_list, available_link_list, assigned_capacity, t, K, p, q, nodes, quality)

        if solution_list[t].isOptimized():
            print("t: %d, optimal value:\t%8.4f" % (t, solution_list[t].optimal_value))
            return solution_list[t].optimal_value, t
        else:
            # 上
            if direction >= 0:
                if t + 1 <= maximum_time:
                    print("shifted to %d" % (t + 1))
                    return self.GetObjVal(solution_list, link_list, available_link_list, required_total_capacity, t + 1, K, p, q, nodes, quality, minimum_time, maximum_time, 1)
            # 下
            if direction <= 0:
                if minimum_time <= t - 1:
                    print("shifted to %d" % (t - 1))
                    return self.GetObjVal(solution_list, link_list, available_link_list, required_total_capacity, t - 1, K, p, q, nodes, quality, minimum_time, maximum_time, -1)
            return False

    def calc_path_reliability(self, nodes, link_list, holding_time):
        reliable_probability = 1.0
        for i in range(len(nodes) -1):
            reliable_probability = reliable_probability * link_list[(nodes[i], nodes[i + 1])].calculate_reliability(holding_time)
        return reliable_probability
    
    def dfs(self, p, q, available_link_list, now_node, node_sequence, path_probability, link_list):
        if now_node == q:
            print(node_sequence + [now_node])
            path_probability[tuple(node_sequence + [now_node])] =self.calc_path_reliability(node_sequence, link_list, self.holding_time)
        else:
            for (ix, jx) in available_link_list:
                if ix == now_node:
                    if not jx in node_sequence:
                        self.dfs(p, q, available_link_list, jx, node_sequence + [now_node], path_probability, link_list)

    def CalcRoute(self, solution, routing_type, max_route_num, node_size, link_list, available_link_list, ks = 1):
        """

        :type solution: Solution
        :type routing_type: RouteCalcType
        :type max_route_num: int
        :type node_size: int
        :type link_list: dict[tuple[int, int], Link]
        :type available_link_list: list[tuple[int, int]]
        :return:
        """
        M = max_route_num  # 経路数
        p = self.start_node  # 起点
        q = self.end_node  # 終点
        required_capacity = self.bandwidth
        quality = self.quality

        K = range(1, M + 1)
        nodes = range(1, node_size + 1)
        bandwidth_max = 0

        # print "%s:\t%8.4f" % (x[i, j].VarName, x[i, j].X)
        if routing_type == RouteCalcType.ExpectedCapacityGuarantee:
            m = grb.Model()
            variables = RouteCalcVariables()
            m.setParam('OutputFlag', False)
            m.setParam('TimeLimit', 200)

            # 変数追加
            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    available_link_list.append((i, j))
                    for k in K:
                        # print("x[k, i, j] = x[{}, {}, {}]".format(k, i, j))
                        variables.x[k, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="x_{%d,%d,%d}" % (k, i, j))
                        variables.y[k, i, j] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="y_{%d,%d,%d}" % (k, i, j))
            for k in K:
                variables.b[k] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="b_{%d}" % k)

            # 完全に同じ経路にさせないようにするための条件　変数追加
            for k in K:
                for kk in K:
                    if k != kk:
                        for (i, j) in available_link_list:
                            # variables.a[k, kk, i, j] = m.addVar(vtype = grb.GRB.BINARY, name = "a_{%d,$d,%d,%d}" % (k, kk, i, j))
                            variables.a[k, kk, i, j] = m.addVar(vtype = grb.GRB.BINARY, name = "a_st1")
                            variables.z[k, kk, i, j] = m.addVar(vtype = grb.GRB.BINARY, name = "a_st2")
                            variables.w[k, kk, i, j] = m.addVar(vtype = grb.GRB.BINARY, name = "a_st3")

            m.update()  # モデルに変数が追加されたことを反映させる
            
            ####### リンク故障率がちゃんと反映されているか確認 ######
            # print("In traffic.py CalcRoute()..., ")
            # for (i, j) in available_link_list:
            #     print("{} -> {}, reliability: {}".format(i, j, link_list[(i, j)].calculate_reliability(self.holding_time)))
            # print("")
            ######################################################


            # 目的関数を設定し，最小化を行うことを明示する
            m.setObjective(grb.quicksum(
                grb.quicksum(variables.y[k, i, j] * link_list[(i, j)].distance for (i, j) in available_link_list)
                for k in K),
                grb.GRB.MINIMIZE)  # 目的関数
            # m.setAttr("ModelSense", grb.GRB.MINIMIZE)

            # 制約追加
            for i in nodes:
                if i == p:
                    for k in K:
                        m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                    - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list)
                                    == 1, name="flow reservation at node %d route %d" % (i, k))
                if i != p and i != q:
                    for k in K:
                        m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                    - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list)
                                    == 0, name="flow reservation at node %d route %d" % (i, k))

            for (i, j) in available_link_list:
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))
                # gurobi9.0以降
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= link_list[(i, j)].bandwidth, name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(grb.quicksum(variables.y[k, i, j] for k in K) <= link_list[(i, j)].bandwidth, name="capacity requirement at (%d, %d)" % (i, j))  # min()いると思われ?

            m.addConstr(grb.quicksum(variables.b[k] for k in K) >= required_capacity, name="required capacity requirement")
            m.addConstr(grb.quicksum(variables.b[k] for k in K) - grb.quicksum(
                grb.quicksum(
                    (1 - link_list[(i, j)].calculate_reliability(self.holding_time)) * variables.y[k, i, j] for (i, j) in available_link_list) for k in K) >= quality * required_capacity,
                        name="expected capacity requirement")

            for k in K:
                for (i, j) in available_link_list:
                    m.addConstr(variables.y[k, i, j] >= variables.b[k] + (bandwidth_max * (variables.x[k, i, j] - 1)), name="st1 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] <= link_list[(i, j)].bandwidth * variables.x[k, i, j], name="st2 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] >= 0, name="st3 at (%d, %d) route %d" % (i, j, k))

            # 完全に同じ経路にさせないための条件　制約
            for k in K:
                if k <= 2:
                    m.addConstr(variables.b[k] >= 1, name = "route capacity k = 1, 2")
                else:
                    m.addConstr(variables.b[k] >= 0, name = "route capacity k >= 3")

            for k in K:
                for kk in K:
                    if k != kk:
                        for (i, j) in available_link_list:
                            m.addConstr(variables.a[k, kk, i, j] * 2 >= 2 - variables.x[k, i, j] - variables.x[kk, i, j], name = "st1 a_{%d,%d,%d,%d}" % (k, kk, i, j))
                            m.addConstr(variables.a[k, kk, i, j] <= 2 - variables.x[k, i, j] - variables.x[kk, i, j], name = "st2 a_{%d,%d,%d,%d}" % (k, kk, i, j))
                            m.addConstr(variables.z[k, kk, i, j] * 2 >= variables.x[k, i, j] + variables.x[kk, i, j], name = "st1 z_{%d,%d,%d,%d}" % (k ,kk, i, j))
                            m.addConstr(variables.z[k, kk, i, j] <= variables.x[k, i, j] + variables.x[kk, i, j], name = "st2 z_{%d,%d,%d,%d}" % (k, kk, i, j))
                            m.addConstr(variables.w[k, kk, i, j] <= variables.a[k, kk, i, j], name = "st1 w_{%d,%d,%d,%d}" % (k, kk, i, j))
                            m.addConstr(variables.w[k, kk, i, j] <= variables.z[k, kk, i, j], name = "st2 w_{%d,%d,%d,%d}" % (k, kk, i, j))
                            m.addConstr(variables.w[k, kk, i, j] >= variables.a[k, kk, i, j] + variables.z[k, kk, i, j] - 1, name = "st3 w_{%d,%d,%d,%d}" % (k, kk, i, j))
            
            for k in K:
                for kk in K:
                    if k != kk:
                        m.addConstr(grb.quicksum(variables.w[k, kk, i, j] for (i, j) in available_link_list) >= 1)
            
            for k in K:
                m.addConstr(variables.b[k] <= self.bandwidth * 0.5, name = "path capacity constraction")

            # モデルに制約条件が追加されたことを反映させる
            m.update()

            m.optimize()
            solution.setValues(m, variables, self.holding_time)



        elif routing_type == RouteCalcType.MinCostFlow:
            m = grb.Model()
            variables = RouteCalcVariables()
            m.setParam('OutputFlag', False)
            m.setParam('TimeLimit', 100)

            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    available_link_list.append((i, j))
                    for k in K:
                        variables.x[k, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="x_{%d,%d,%d}" % (k, i, j))
                        variables.y[k, i, j] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER,
                                                        name="y_{%d,%d,%d}" % (k, i, j))
            for k in K:
                variables.b[k] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="b_{%d}" % k)

            m.update()  # モデルに変数が追加されたことを反映させる

            # 目的関数を設定し，最小化を行うことを明示する
            m.setObjective(grb.quicksum(grb.quicksum(variables.y[k, i, j] * link_list[(i, j)].distance for (i, j) in available_link_list) for k in K), grb.GRB.MINIMIZE)  # 目的関数
            # m.setAttr("ModelSense", grb.GRB.MINIMIZE)

            # 制約追加
            for i in nodes:
                if i == p:
                    for k in K:
                        m.addConstr(
                            grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                            - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list) == 1, name="flow reservation at node %d route %d" % (i, k))
                if i != p and i != q:
                    for k in K:
                        m.addConstr(
                            grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                            - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list) == 0, name="flow reservation at node %d route %d" % (i, k))

            for (i, j) in available_link_list:
                # gurobi9.0以降
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))
            for k in K:
                m.addConstr(variables.b[k] <= required_capacity, name="route %d requirement" % k)
                m.addConstr(grb.quicksum(variables.b[k] for k in K) >= required_capacity, name="required capacity requirement")
            for k in K:
                for (i, j) in available_link_list:
                    m.addConstr(variables.y[k, i, j] >= variables.b[k] + (bandwidth_max * (variables.x[k, i, j] - 1)), name="st1 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] <= link_list[(i, j)].bandwidth * variables.x[k, i, j], name="st2 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] >= 0, name="st3 at (%d, %d) route %d" % (i, j, k))

            # モデルに制約条件が追加されたことを反映させる
            m.update()
            # 最適化を行い，結果を表示させる
            # m.write("mincostflow.lp")  # mincostflow.lp というファイルに定式化されたモデルを出力する
            m.optimize()
            solution.setValues(m, variables, self.holding_time)
        elif routing_type == RouteCalcType.Backup:
            m = grb.Model()
            variables = RouteCalcVariables()
            m.setParam('OutputFlag', False)
            m.setParam('TimeLimit', 100)

            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    available_link_list.append((i, j))
                    for k in K:
                        variables.x[k, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="x_{%d,%d,%d}" % (k, i, j))
                        variables.y[k, i, j] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="y_{%d,%d,%d}" % (k, i, j))
            for k in K:
                variables.b[k] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="b_{%d}" % k)

            m.update()  # モデルに変数が追加されたことを反映させる

            # 目的関数を設定し，最小化を行うことを明示する
            m.setObjective(grb.quicksum(grb.quicksum(variables.y[k, i, j] * link_list[(i, j)].distance for (i, j) in available_link_list) for k in K), grb.GRB.MINIMIZE)  # 目的関数
            # m.setAttr("ModelSense", grb.GRB.MINIMIZE)

            # 制約追加
            for i in nodes:
                if i == p:
                    for k in K:
                        m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                    - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list) == 1, name="flow reservation at node %d route %d" % (i, k))
                if i != p and i != q:
                    for k in K:
                        m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                    - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list) == 0, name="flow reservation at node %d route %d" % (i, k))

            for (i, j) in available_link_list:
                #gurobi9.0以降
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))

            m.addConstr(variables.b[1] >= required_capacity, name="main route capacity requirement")

            for k in K:
                if k != 1:
                    m.addConstr(variables.b[k] >= self.quality * self.bandwidth,
                                name="backup route capacity requirement")

            for (i, j) in available_link_list:
                for k1 in K:
                    for k2 in K:
                        if k1 != k2:
                            m.addConstr(variables.x[k1, i, j] + variables.x[k2, i, j] <= 1, name="disjoint requirement at (%d, %d) for route %d, %d" % (i, j, k1, k2))

            for k in K:
                for (i, j) in available_link_list:
                    m.addConstr(variables.y[k, i, j] >= variables.b[k] + (bandwidth_max * (variables.x[k, i, j] - 1)), name="st1 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] <= link_list[(i, j)].bandwidth * variables.x[k, i, j], name="st2 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] >= 0, name="st3 at (%d, %d) route %d" % (i, j, k))
            # モデルに制約条件が追加されたことを反映させる
            m.update()
            # 最適化を行い，結果を表示させる
            # m.write("mincostflow.lp")  # mincostflow.lp というファイルに定式化されたモデルを出力する

            m.optimize()
            solution.setValues(m, variables, self.holding_time)
        elif routing_type == RouteCalcType.KshortestExpectedCapacityGuarantee:
            try:
                f = open('topology_mesh.txt', 'r')
                line = f.readline()  # 1行を文字列として読み込む(改行文字も含まれる)
                # ノード集合
                node_list = []
                line = f.readline()

                while line:
                    data = line[:-1].split(' ')
                    if len(data) == 3 and data[0].isdigit() and data[1].isdigit() and data[2].isdigit():
                        if int(data[0]) not in node_list:
                            node_list.append(int(data[0]))
                        if int(data[1]) not in node_list:
                            node_list.append(int(data[1]))
                    line = f.readline()
                f.close()
            except Exception as e:
                print("node cannot be read.")
            a = []
            bb = []
            tmp = []
            tmpz = []
            route_list = [[0] * 500 for i in range(500)]
            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    route_list[i][j] = link_item.distance
                    route_list[j][i] = link_item.distance
            path, cost = self.dijkstra(route_list, p, q)
            tmpz.append(path)
            tmpz.append(cost)
            a.append(tmpz)
            for xx in range(ks):
                path = copy.deepcopy(a[xx])
                for y in range(len(path[0]) - 1):
                    for (i, j), link_item in link_list.items():
                        if link_item.failure_status == 0:
                            bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                            route_list[i][j] = link_item.distance
                            route_list[j][i] = link_item.distance

                    for F in range(xx + 1):
                        for uio in range(len(a[F][0]) - 1):
                            if path[0][y] == a[F][0][uio]:
                                route_list[a[F][0][uio]][a[F][0][uio + 1]] = math.inf
                                route_list[a[F][0][uio + 1]][a[F][0][uio]] = math.inf
                                break
                    pathzz, costzz = self.dijkstra(route_list, p, path[0][y])
                    pathz, costz = self.dijkstra(route_list, path[0][y], q)
                    if len(pathz) != 0:
                        pathz.pop(0)
                    tmp = []
                    ##tmp.clear()
                    tmp.append(pathzz + pathz)
                    tmp.append(costzz + costz)
                    flag = 0
                    for mats in bb:
                        if mats[0] == tmp[0]:
                            flag = 1
                    if flag == 0:
                        bb.append(tmp)

                minn = math.inf
                min_index = 0
                for zz in range(len(bb)):
                    if (minn > bb[zz][1]):
                        minn = bb[zz][1]
                        min_index = zz
                try:
                    a.append(bb[min_index])
                    bb.pop(min_index)
                except Exception as e:
                    break
            node_list_cnt = [0] * 500
            node_list_re = []
            for n in a:
                for m in n[0]:
                    node_list_cnt[m] += 1
            for n in range(500):
                if node_list_cnt[n] != 0:
                    node_list_re.append(n)

            m = grb.Model()
            variables = RouteCalcVariables()
            m.setParam('OutputFlag', False)
            m.setParam('TimeLimit', 100)
            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0 and i in node_list_re and j in node_list_re:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    available_link_list.append((i, j))
                    for k in K:
                        variables.x[k, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="x_{%d,%d,%d}" % (k, i, j))
                        variables.y[k, i, j] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="y_{%d,%d,%d}" % (k, i, j))
            for k in K:
                variables.b[k] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="b_{%d}" % k)

            m.update()  # モデルに変数が追加されたことを反映させる

            # 目的関数を設定し，最小化を行うことを明示する
            m.setObjective(grb.quicksum(
                grb.quicksum(variables.y[k, i, j] * link_list[(i, j)].distance for (i, j) in available_link_list)
                for k in K),
                grb.GRB.MINIMIZE)  # 目的関数

            # 制約追加
            for i in node_list_re:
                if i == p:
                    for k in K:
                        m.addConstr(
                            grb.quicksum(variables.x[k, i, j] for j in node_list if (i, j) in available_link_list)
                            - grb.quicksum(variables.x[k, j, i] for j in node_list if (j, i) in available_link_list)
                            == 1, name="flow reservation at node %d route %d" % (i, k))
                if i != p and i != q:
                    for k in K:
                        m.addConstr(
                            grb.quicksum(variables.x[k, i, j] for j in node_list if (i, j) in available_link_list)
                            - grb.quicksum(variables.x[k, j, i] for j in node_list if (j, i) in available_link_list)
                            == 0, name="flow reservation at node %d route %d" % (i, k))
            for (i, j) in available_link_list:
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))
                #gurobi9.0以降
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= link_list[(i, j)].bandwidth,name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(grb.quicksum(variables.y[k, i, j] for k in K) <= link_list[(i, j)].bandwidth, name="capacity requirement at (%d, %d)" % (i, j))

            m.addConstr(grb.quicksum(variables.b[k] for k in K) >= required_capacity,
                        name="required capacity requirement")
            m.addConstr(grb.quicksum(variables.b[k] for k in K) - grb.quicksum(
                grb.quicksum(
                    (1 - link_list[(i, j)].calculate_reliability(self.holding_time)) * variables.y[k, i, j] for (i, j) in
                    available_link_list) for k in K) >= required_capacity,
                        name="expected capacity requirement")

            for k in K:
                for (i, j) in available_link_list:
                    m.addConstr(variables.y[k, i, j] >= variables.b[k] + (bandwidth_max * (variables.x[k, i, j] - 1)),
                                name="st1 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] <= link_list[(i, j)].bandwidth * variables.x[k, i, j],
                                name="st2 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] >= 0, name="st3 at (%d, %d) route %d" % (i, j, k))

            # モデルに制約条件が追加されたことを反映させる
            m.update()
            # 最適化を行い，結果を表示させる
            # m.write("mincostflow.lp")  # mincostflow.lp というファイルに定式化されたモデルを出力する

            m.optimize()
            solution.setValues(m, variables, self.holding_time)
        elif routing_type == RouteCalcType.AdaptableExpectedCapacityGuarantee:
            solution_list = {}  # type: dict[int, Solution]
            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    available_link_list.append((i, j))
            minimum_cost = sys.maxsize
            optimal_time = 0
            start_time = 1
            required_total_capacity = self.bandwidth * self.holding_time
            end_time = required_total_capacity
            delta = math.ceil((end_time - start_time) / 2)
            if delta == 0:
                delta = 1
            result = self.doCalcRange(solution_list, required_total_capacity, link_list, available_link_list, delta, end_time + 1, start_time, end_time + 1, start_time, K, p, q, nodes,
                                      quality)
            print("min %d max %d" % (result[0], result[1]))

            start_time_sol = result[0]
            end_time_sol = result[1]

            if start_time_sol > end_time_sol:
                # 解なし
                print("No Optimal")
                solution_list[end_time_sol].copy(solution)
                return end_time_sol

            optimal_time = -1
            if optimal_time == -1:
                minimum_val = sys.maxsize
                # どうにもならないときに線形探索
                print("Liner Discovery")
                print("p: %d q: %d required_total_capacity: %d" % (p, q, required_total_capacity))
                for t in range(start_time_sol, end_time_sol + 1):
                    objVal = self.GetObjVal(solution_list, link_list, available_link_list, required_total_capacity, t, K, p, q, nodes, quality, t, t)
                    if objVal:
                        if objVal[0] < minimum_val:
                            minimum_val = objVal[0]
                            optimal_time = objVal[1]
                if optimal_time == -1:
                    print("No Optimal")
                    solution_list[end_time_sol].copy(solution)
                    return end_time_sol
                else:
                    print("Optimal Found: %d" % optimal_time)
                    solution_list[optimal_time].copy(solution)
                    return optimal_time
            else:
                solution_list[optimal_time].copy(solution)
                print("minimum cost %.5f time: %d" % (minimum_cost, optimal_time))
                return optimal_time

        elif routing_type == RouteCalcType.Multipath: ## マルチパス
            m = grb.Model()
            variables = RouteCalcVariables()
            m.setParam('OutputFlag', False)
            m.setParam('TimeLimit', 100)

            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    bandwidth_max = max([link_item.bandwidth, bandwidth_max])
                    available_link_list.append((i, j))
                    for k in K:
                        variables.x[k, i, j] = m.addVar(vtype=grb.GRB.BINARY, name="x_{%d,%d,%d}" % (k, i, j))
                        variables.y[k, i, j] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="y_{%d,%d,%d}" % (k, i, j))
            for k in K:
                variables.b[k] = m.addVar(lb=0.0, vtype=grb.GRB.INTEGER, name="b_{%d}" % k)

            m.update()  # モデルに変数が追加されたことを反映させる

            # 目的関数を設定し，最小化を行うことを明示する
            m.setObjective(grb.quicksum(grb.quicksum(variables.y[k, i, j] * link_list[(i, j)].distance for (i, j) in available_link_list) for k in K), grb.GRB.MINIMIZE)  # 目的関数
            # m.setAttr("ModelSense", grb.GRB.MINIMIZE)

            # 制約追加
            for i in nodes:
                if i == p:
                    for k in K:
                        m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                    - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list) == 1, name="flow reservation at node %d route %d" % (i, k))
                if i != p and i != q:
                    for k in K:
                        m.addConstr(grb.quicksum(variables.x[k, i, j] for j in nodes if (i, j) in available_link_list)
                                    - grb.quicksum(variables.x[k, j, i] for j in nodes if (j, i) in available_link_list) == 0, name="flow reservation at node %d route %d" % (i, k))

            for (i, j) in available_link_list:
                #gurobi9.0以降
                # m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(0 <= grb.quicksum(variables.y[k, i, j] for k in K), name="capacity requirement at (%d, %d)" % (i, j))
                m.addConstr(grb.quicksum(variables.y[k, i, j] for k in K) <= min(link_list[(i, j)].bandwidth, required_capacity), name="capacity requirement at (%d, %d)" % (i, j))

            for k in K:
                m.addConstr(variables.b[k] >= self.quality * self.bandwidth, name = "all(sub)-path capacity requirement")


            for (i, j) in available_link_list:
                m.addConstr(grb.quicksum(variables.x[k, i, j] for k in K) <= 1, name = "disjoing requirement at (%d, %d) for route %d" % (i, j, k))

            for k in K:
                for (i, j) in available_link_list:
                    m.addConstr(variables.y[k, i, j] >= variables.b[k] + (bandwidth_max * (variables.x[k, i, j] - 1)), name="st1 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] <= link_list[(i, j)].bandwidth * variables.x[k, i, j], name="st2 at (%d, %d) route %d" % (i, j, k))
                    m.addConstr(variables.y[k, i, j] >= 0, name="st3 at (%d, %d) route %d" % (i, j, k))
            # モデルに制約条件が追加されたことを反映させる
            m.update()
            # 最適化を行い，結果を表示させる
            # m.write("mincostflow.lp")  # mincostflow.lp というファイルに定式化されたモデルを出力する

            m.optimize()
            solution.setValues(m, variables, self.holding_time)

        elif routing_type == RouteCalcType.OkumuraECGR: ###################### okumura ecgr ###########################
            ## MILPを使わずに容量を確保する
            ## 全パスの故障確率を求めた後、各経路確保する容量を決定
            ## 
            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    available_link_list.append((i, j))

            path_probability  = {}  ##dict{(nodes): probability}
            
            self.dfs(p, q, available_link_list, p, [], path_probability, link_list)
            # print("dfs is done")
            # print("---path_probability---")
            # print(path_probability)

            # for (i1, j1) in available_link_list:
            #     if i1 == p:
            #         node1 = i1
            #         if j1 == q:
            #             node2 = j1
            #             # route_list.append((node1, node2))
            #             path_probability[(node1, node2)] = self.calc_path_reliability((node1, node2), link_list, self.holding_time)
            #             # print(node1, node2)
            #         else:
            #             node2 = j1
            #             for (i2, j2) in available_link_list:
            #                 if i2 == j1 and j2 != node1 and j2 != node2:
            #                     if j2 == q:
            #                         node3 = j2
            #                         # route_list.append((node1, node2, node3))
            #                         path_probability[(node1, node2, node3)] = self.calc_path_reliability((node1, node2, node3), link_list, self.holding_time)
            #                         # print(node1, node2, node3)
            #                     else:
            #                         node3 = j2
            #                         for (i3, j3) in available_link_list:
            #                             if i3 == j2 and j3 != node1 and j3 !=node2 and j3 != node3:
            #                                 if j3 == q:
            #                                     node4 = j3
            #                                     # route_list.append((node1, node2, node3, node4))
            #                                     path_probability[(node1, node2, node3, node4)] = self.calc_path_reliability((node1, node2, node3, node4), link_list, self.holding_time)
            #                                     # print(node1, node2, node3, node4)
            #                                 else:
            #                                     node4 = j3
            #                                     for (i4, j4) in available_link_list:
            #                                         if i4 == j3 and j4 != node1 and j4 != node2 and j4 != node3 and j4 != node4:
            #                                             if j4 == q:
            #                                                 node5 = j4
            #                                                 # route_list.append((node1, node2, node3, node4, node5))
            #                                                 path_probability[(node1, node2, node3, node4, node5)] = self.calc_path_reliability((node1, node2, node3, node4, node5), link_list, self.holding_time)
            #                                                 # print(node1, node2, node3, node4, node5)
            #                                             else:
            #                                                 print("route setting error")
            
            max_key = max(path_probability, key = path_probability.get)
            variables = RouteCalcVariables()
            for (i, j), link_item in link_list.items():
                if link_item.failure_status == 0:
                    for k in K:
                        variables.x[k, i, j] = 0
                        variables.y[k, i, j] = 0

            for k in K:
                variables.b[k] = 0

            expected_capacity = 0
            actual_capacity = 0
            path_capacity_limit = 0.8
            usable_path = 0

            for number in range(len(path_probability)):
                max_key = max(path_probability, key = path_probability.get)

                print("{} {}".format(max_key, path_probability[max_key]))

                ## ここでパス中の最小リンク容量をpath_min_capacityへ代入
                path_min_capacity = 999999
                print("path number : {} / {}".format(number + 1, len(K)))
                
                for i in range(len(max_key) - 1):
                    previous = 0
                    # for kk in range(1, number + 1):
                    for kk in range(1, usable_path + 1):
                        previous += variables.y[kk, max_key[i], max_key[i + 1]]
                    if path_min_capacity >= link_list[(max_key[i], max_key[i + 1])].bandwidth - previous:
                        path_min_capacity = link_list[(max_key[i], max_key[i + 1])].bandwidth - previous
                print("remaining path capacity : {}".format(path_min_capacity))

                ## もしpath_min_capacityが１経路あたりの最大容量よりも大きい場合
                reserve_capacity = 0
                if path_min_capacity >= required_capacity * path_capacity_limit:
                    reserve_capacity = required_capacity * path_capacity_limit
                else:
                    reserve_capacity = path_min_capacity
                
                ## 必要以上に容量を確保しないように調整
                if expected_capacity + reserve_capacity * self.calc_path_reliability(max_key, link_list, self.holding_time) > required_capacity * quality:
                    reserve_capacity = math.ceil((required_capacity * quality - expected_capacity) / self.calc_path_reliability(max_key, link_list, self.holding_time))

                ## 容量0以上とれたら使えるパス認定
                if reserve_capacity > 0:
                    usable_path += 1
                
                    ## 容量期待値、実際の容量を加算
                    expected_capacity += reserve_capacity * self.calc_path_reliability(max_key, link_list , self.holding_time)
                    actual_capacity += reserve_capacity
                    print("path[{}] current EC = {}, actulal C = {}".format(usable_path, expected_capacity, actual_capacity))

                    ## variable x,y,bへ代入
                    for j in range(len(max_key) - 1):
                        variables.x[usable_path, max_key[j], max_key[j + 1]] = 1
                        variables.y[usable_path, max_key[j], max_key[j + 1]] = reserve_capacity
                    variables.b[usable_path] = reserve_capacity
                    
                ## 容量期待値が要求容量×Qを超えれば終わり
                if expected_capacity > required_capacity * quality:
                    break
                
                ## 容量0以上とれた経路数がlen(K)に達したら終わり
                if usable_path >= len(K):
                    break
                # if number + 1 >= len(K):
                #     break

                ## 扱った最大信頼確率をもつパスを消去
                del path_probability[max_key]

            # m = grb.Model()
            
            if expected_capacity < required_capacity * quality:
                print("Blocked !!")
                solution.setValues_okumura(False, variables, self.holding_time)
            else:
                print("ok")
                solution.setValues_okumura(True, variables, self.holding_time)
            
        else:
            return False

        return self.holding_time
