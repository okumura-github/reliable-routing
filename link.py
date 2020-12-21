import math
import random as rnd
import numpy
import sys


class Link:
    # Define
    # LOG_FILE = "log.txt"
    # LOG_FILE2 = "log2.txt"
    # LOG_FILE3 = "log3.txt"
    # LOG_FILE4 = "log4.txt"
    LOG_FILE = "log_ecgr.txt"
    LOG_FILE2 = "log_mincost.txt"
    LOG_FILE3 = "log_dpp.txt"
    LOG_FILE4 = "log_kshortest.txt"
    LOG_FILE5 = "log_mpp50%.txt"
    LOG_FILE6 = "log_mpp40%.txt"
    LOG_FAIL = "log_fail_repair.txt"
    LOG_FAIL_RATE = "log_fail_rate.txt"

    def __init__(self, distance=0,
                 bandwidth=0, failure_rate=0.0, failure_status=0, shape=1, scale=0, age=0):
        """

        :param distance: int
        :param bandwidth: int
        :param failure_rate: float
        :param failure_status: int
        :param shape: int
        :param scale: int
        """
        self.distance = distance
        self.bandwidth = bandwidth
        self.initial_bandwidth = bandwidth
        self.failure_rate = failure_rate
        self.failure_status = failure_status
        self.shape = shape
        self.scale = scale
        self.age = age

    def calculate_reliability(self, holding_time):
        """

        :type holding_time: int
        :return:
        """
        # reliability_old = math.exp((pow(self.age, self.shape) - pow(self.age + holding_time, self.shape)) / pow(self.scale, self.shape))
        # fraction = 1
        # denominator = 1
        # for i in range(1, self.age + holding_time + 1):
        #     pdf = self.get_weibull_pdf(self.shape, self.scale, i)
        #     fraction -= pdf
        #     if i <= self.age:
        #         denominator -= pdf
        # reliability = fraction / denominator

        # print("In calculate_reliability..., shape: {}, scale: {}".format(self.shape, self.scale))
        
        reliability = 1
        nofailure_rate = 1
        for i in range(self.age, self.age + holding_time):
            failure_rate = nofailure_rate * self.get_weibull_failure_rate(self.shape, self.scale, i)
            reliability -= failure_rate
            if reliability < 0:
                return 0
            nofailure_rate *= 1 - self.get_weibull_failure_rate(self.shape, self.scale, i)

        return reliability

    def update_link_failure_rate(self):
        """
        :return:
        """
        failure_rate = self.get_weibull_failure_rate(self.shape, self.scale, self.age)
        self.failure_rate = failure_rate

    def add_age(self):
        self.age += 1

    def reset(self, shape=1, scale=1):
        self.shape = shape
        self.scale = scale
        self.failure_rate = 0.0
        self.failure_status = 0
        self.age = 0

    @staticmethod
    def get_weibull_failure_rate(shape, scale, t):
        """

        :param shape: float
        :param scale: float
        :param t: float
        :return: float
        """
        # print("%d:%d:%d\n" %(shape,scale,t))
        failure_rate = ((shape * pow(t, (shape - 1))) / pow(scale, shape))
        if failure_rate >= 1:
            return 1
        return failure_rate

    @staticmethod
    def get_weibull_pdf(shape, scale, t):
        """

                :param shape: float
                :param scale: float
                :param t: float
                :return: float
                """
        # print("%d:%d:%d\n" %(shape,scale,t))
        pdf = (shape / scale) * math.pow((t / scale), shape - 1) * math.exp(-1 * math.pow((t / scale), shape))
        return pdf

    @staticmethod
    def is_failure(p_failure_rate):
        random = numpy.random.rand()
        return p_failure_rate > random

    @staticmethod
    def is_repaired(p_ave_repaired_time, p_failure_time):
        repaire_probability = 1.0 - math.exp(-1.0 * (1.0 / p_ave_repaired_time) * p_failure_time)
        random = rnd.random()
        return repaire_probability > random

    @classmethod
    def write_log(cls, msg):
        try:
            f = open(cls.LOG_FILE, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FILE), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log(msg)

    @classmethod
    def write_log2(cls, msg):
        try:
            f = open(cls.LOG_FILE2, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FILE2), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log2(msg)

    @classmethod
    def write_log3(cls, msg):
        try:
            f = open(cls.LOG_FILE3, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FILE3), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log3(msg)

    @classmethod
    def write_log4(cls, msg):
        try:
            f = open(cls.LOG_FILE4, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FILE4), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log4(msg)

    @classmethod
    def write_log5(cls, msg):
        try:
            f = open(cls.LOG_FILE5, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FILE5), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log5(msg)

    @classmethod
    def write_log6(cls, msg):
        try:
            f = open(cls.LOG_FILE6, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FILE6), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log6(msg)

    @classmethod
    def write_log_fail(cls, msg):
        try:
            f = open(cls.LOG_FAIL, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FAIL), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log_fail(msg)
    
    @classmethod
    def write_log_fail_rate(cls, msg):
        try:
            f = open(cls.LOG_FAIL_RATE, 'a')
            f.write(msg)
            f.close()
        except IOError as e:
            print('except: Cannot open "{0}"'.format(cls.LOG_FAIL_RATE), file=sys.stderr)
            print('  errno: [{0}] msg: [{1}]'.format(e.errno, e.strerror), file=sys.stderr)
            cls.write_log_fail_rate(msg)

    def get_scale_rand(self):
        if self.scale == 0:
            return 10
        else:
            return self.scale
            # i = rnd.randint(0, 2)
            # if i == 0:
            #     return 100
            # if i == 1:
            #     return 33
            # if i == 2:
            #     return 20
            # else:
            #     return 100

    @classmethod
    def process_link_status(cls, link_list, link_list2, link_list3, link_list4, link_list5, link_list6, traffic_list, traffic_list2, traffic_list3, traffic_list4, traffic_list5, traffic_list6, average_repaired_time):
        # リンク障害判定
        for link_item_key, link_item in link_list.items():
            if link_item is not None:
                if link_item.failure_status == 0:
                    # リンク故障していないとき
                    # リンク故障率更新
                    link_item.update_link_failure_rate()
                    # if link_item_key[0] == 1 and link_item_key[1] == 2:
                    #     print("age:%d, failure_rate:%f" % (link_item.age, link_item.failure_rate))

                    if cls.is_failure(link_item.failure_rate):
                        # リンク故障判定
                        link_item.failure_status += 1
                        cls.write_log("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list2[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log2("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list3[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log3("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list4[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log4("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list5[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log5("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list6[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log6("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))

                        # 使用中リンクのダウン設定(期待値型ルーティング)
                        for active_traffic_item in traffic_list:
                            expected_bandwidth = active_traffic_item.traffic.bandwidth * active_traffic_item.traffic.quality  # 帯域幅期待値
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log("Link %d->%d add bandwidth: %d\n" % (failed_route_link_key[0], failed_route_link_key[1], failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n"
                                    #               % (active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
                                    #                  active_traffic_item.traffic.end_node, active_traffic_item.traffic.bandwidth,
                                    #                  active_traffic_item.traffic.quality, total_bandwidth))

                        # 使用中リンクのダウン設定(最小費用流)
                        for active_traffic_item in traffic_list2:
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list2[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log2("Link %d->%d add bandwidth: %d\n" % (failed_route_link_key[0], failed_route_link_key[1], failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log2("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n" % (
                                    #         active_traffic_item.traffic.id, active_traffic_item.traffic.start_node, active_traffic_item.traffic.end_node, active_traffic_item.traffic.bandwidth,
                                    #         active_traffic_item.traffic.quality, total_bandwidth))

                        # 使用中リンクのダウン設定(バックアップ)
                        for active_traffic_item in traffic_list3:
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list3[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log3("Link %d->%d add bandwidth: %d\n" % (
                                                failed_route_link_key[0], failed_route_link_key[1],
                                                failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log3("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n"
                                    #                % (
                                    #                    active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
                                    #                    active_traffic_item.traffic.end_node,
                                    #                    active_traffic_item.traffic.bandwidth,
                                    #                    active_traffic_item.traffic.quality, total_bandwidth))
                        # 使用中リンクのダウン設定(adaptable)
                        for active_traffic_item in traffic_list4:
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list4[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log4("Link %d->%d add bandwidth: %d\n" % (
                                                failed_route_link_key[0], failed_route_link_key[1],
                                                failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log3("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n"
                                    #                % (
                                    #                    active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
                                    #                    active_traffic_item.traffic.end_node,
                                    #                    active_traffic_item.traffic.bandwidth,
                                    #                    active_traffic_item.traffic.quality, total_bandwidth))
                        
                        # 使用中リンクのダウン設定(MPP 50% 3本)
                        for active_traffic_item in traffic_list5:
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list5[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log5("Link %d->%d add bandwidth: %d\n" % (
                                                failed_route_link_key[0], failed_route_link_key[1],
                                                failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log5("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n"
                                    #                % (
                                    #                    active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
                                    #                    active_traffic_item.traffic.end_node,
                                    #                    active_traffic_item.traffic.bandwidth,
                                    #                    active_traffic_item.traffic.quality, total_bandwidth))
                        
                        # 使用中リンクのダウン設定(MPP 40% 3本)
                        for active_traffic_item in traffic_list6:
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list6[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log6("Link %d->%d add bandwidth: %d\n" % (
                                                failed_route_link_key[0], failed_route_link_key[1],
                                                failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log6("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n"
                                    #                % (
                                    #                    active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
                                    #                    active_traffic_item.traffic.end_node,
                                    #                    active_traffic_item.traffic.bandwidth,
                                    #                    active_traffic_item.traffic.quality, total_bandwidth))


                    else:
                        # 年齢加算
                        link_item.add_age()
                        link_list2[(link_item_key[0], link_item_key[1])].add_age()
                        link_list3[(link_item_key[0], link_item_key[1])].add_age()
                        link_list4[(link_item_key[0], link_item_key[1])].add_age()
                        link_list5[(link_item_key[0], link_item_key[1])].add_age()
                        link_list6[(link_item_key[0], link_item_key[1])].add_age()

                else:
                    # リンク故障しているとき
                    if cls.is_repaired(average_repaired_time, link_item.failure_status):
                        new_shape = link_item.shape
                        new_scale = link_item.scale
                        # 復旧(使用帯域幅解放は実行済み)
                        # リンク故障率再設定
                        cls.write_log("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_item.reset(new_shape, new_scale)
                        cls.write_log2("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list2[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log3("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list3[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log4("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list4[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log5("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list5[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log6("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list6[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                    else:
                        link_item.failure_status += 1
                        
        return


    # new_process_link_status()はあらかじめ作られた故障イベント情報から故障かどうかを判断する
    # なので、故障判定や復旧判定の部分を引数の情報からとってくるようにする
    # 引数(cls, link_list, link_list2, ..., traffic_list, traffic_list2, ..., fail_repair_info(その時間の故障・復旧判定を含むリンク情報))
    @classmethod
    def new_process_link_status(cls, link_list, link_list2, link_list3, link_list4, link_list5, link_list6, traffic_list, traffic_list2, traffic_list3, traffic_list4, traffic_list5, traffic_list6, fail_repair_info, time):
        # リンク障害判定
        for link_item_key, link_item in link_list.items():
            if link_item is not None:
                if link_item.failure_status == 0: # リンク故障していないとき
                    # link_item.update_link_failure_rate() # リンク故障確率を更新しなくてもいいから、これもコメントアウト
                    link_item.failure_rate = fail_repair_info[link_item_key].failure_rate  # 事前故障イベントに合わせた故障率を更新

                    if fail_repair_info[link_item_key].failure_status: ################### ここを引数のfail_repair_infoで動かしてあげる
                        # リンク故障判定
                        link_item.failure_status += 1
                        cls.write_log("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list2[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log2("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list3[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log3("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list4[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log4("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list5[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log5("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list6[(link_item_key[0], link_item_key[1])].failure_status += 1
                        cls.write_log6("[Link failed] %d->%d\n" % (link_item_key[0], link_item_key[1]))

                        # 使用中リンクのダウン設定(期待値型ルーティング)
                        # for active_traffic_item in traffic_list:
                        #     expected_bandwidth = active_traffic_item.traffic.bandwidth * active_traffic_item.traffic.quality  # 帯域幅期待値
                        #     total_bandwidth = 0
                        #     for route in active_traffic_item.routes[:]:
                        #         del_flag = False
                        #         route_bandwidth = 0
                        #         for route_link_key, route_link_item in route.items():
                        #             route_bandwidth = route_link_item.bandwidth
                        #             if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                        #                 for failed_route_link_key, failed_route_link in route.items():
                        #                     # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                        #                     link_list[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                        #                     cls.write_log("Link %d->%d add bandwidth: %d\n" % (failed_route_link_key[0], failed_route_link_key[1], failed_route_link.bandwidth))
                        #                 del_flag = True
                        #                 break
                        #         if del_flag:
                        #             active_traffic_item.routes.remove(route)
                        #         else:
                        #             total_bandwidth += route_bandwidth
                                    

                        # 使用中リンクのダウン設定(最小費用流)
                        # for active_traffic_item in traffic_list2:
                        #     total_bandwidth = 0
                        #     for route in active_traffic_item.routes[:]:
                        #         del_flag = False
                        #         route_bandwidth = 0
                        #         for route_link_key, route_link_item in route.items():
                        #             route_bandwidth = route_link_item.bandwidth
                        #             if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                        #                 for failed_route_link_key, failed_route_link in route.items():
                        #                     # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                        #                     link_list2[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                        #                     cls.write_log2("Link %d->%d add bandwidth: %d\n" % (failed_route_link_key[0], failed_route_link_key[1], failed_route_link.bandwidth))
                        #                 del_flag = True
                        #                 break
                        #         if del_flag:
                        #             active_traffic_item.routes.remove(route)
                        #         else:
                        #             total_bandwidth += route_bandwidth


                        # 使用中リンクのダウン設定(バックアップ)
                        # for active_traffic_item in traffic_list3:
                        #     total_bandwidth = 0
                        #     for route in active_traffic_item.routes[:]:
                        #         del_flag = False
                        #         route_bandwidth = 0
                                # for route_link_key, route_link_item in route.items():
                                    # route_bandwidth = route_link_item.bandwidth
                                    # if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        # for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            # link_list3[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            # cls.write_log3("Link %d->%d add bandwidth: %d\n" % (
                                            #     failed_route_link_key[0], failed_route_link_key[1],
                                            #     failed_route_link.bandwidth))
                                        # del_flag = True
                                        # break
                                # if del_flag:
                                    # active_traffic_item.routes.remove(route)
                                # else:
                                    # total_bandwidth += route_bandwidth
                                    
                        # 使用中リンクのダウン設定(adaptable)
                        for active_traffic_item in traffic_list4:
                            total_bandwidth = 0
                            for route in active_traffic_item.routes[:]:
                                del_flag = False
                                route_bandwidth = 0
                                for route_link_key, route_link_item in route.items():
                                    route_bandwidth = route_link_item.bandwidth
                                    if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                                        for failed_route_link_key, failed_route_link in route.items():
                                            # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                                            link_list4[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                                            cls.write_log4("Link %d->%d add bandwidth: %d\n" % (
                                                failed_route_link_key[0], failed_route_link_key[1],
                                                failed_route_link.bandwidth))
                                        del_flag = True
                                        break
                                if del_flag:
                                    active_traffic_item.routes.remove(route)
                                else:
                                    total_bandwidth += route_bandwidth
                                    # if total_bandwidth < expected_bandwidth:
                                    #     write_log3("[Bandwidth Lowering(%d)] %d->%d (%d, %f)->%d\n"
                                    #                % (
                                    #                    active_traffic_item.traffic.id, active_traffic_item.traffic.start_node,
                                    #                    active_traffic_item.traffic.end_node,
                                    #                    active_traffic_item.traffic.bandwidth,
                                    #                    active_traffic_item.traffic.quality, total_bandwidth))
                        
                        # 使用中リンクのダウン設定(MPP 50% 3本)
                        # for active_traffic_item in traffic_list5:
                        #     total_bandwidth = 0
                        #     for route in active_traffic_item.routes[:]:
                        #         del_flag = False
                        #         route_bandwidth = 0
                        #         for route_link_key, route_link_item in route.items():
                        #             route_bandwidth = route_link_item.bandwidth
                        #             if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                        #                 for failed_route_link_key, failed_route_link in route.items():
                        #                     # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                        #                     link_list5[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                        #                     cls.write_log5("Link %d->%d add bandwidth: %d\n" % (
                        #                         failed_route_link_key[0], failed_route_link_key[1],
                        #                         failed_route_link.bandwidth))
                        #                 del_flag = True
                        #                 break
                        #         if del_flag:
                        #             active_traffic_item.routes.remove(route)
                        #         else:
                        #             total_bandwidth += route_bandwidth
                                    
                        
                        # 使用中リンクのダウン設定(MPP 40% 3本)
                        # for active_traffic_item in traffic_list6:
                        #     total_bandwidth = 0
                        #     for route in active_traffic_item.routes[:]:
                        #         del_flag = False
                        #         route_bandwidth = 0
                        #         for route_link_key, route_link_item in route.items():
                        #             route_bandwidth = route_link_item.bandwidth
                        #             if link_item_key[0] == route_link_key[0] and link_item_key[1] == route_link_key[1]:
                        #                 for failed_route_link_key, failed_route_link in route.items():
                        #                     # 故障したリンクの存在するルートのすべてのリンクの使用を中断、使用帯域幅解放
                        #                     link_list6[(failed_route_link_key[0], failed_route_link_key[1])].bandwidth += failed_route_link.bandwidth
                        #                     cls.write_log6("Link %d->%d add bandwidth: %d\n" % (
                        #                         failed_route_link_key[0], failed_route_link_key[1],
                        #                         failed_route_link.bandwidth))
                        #                 del_flag = True
                        #                 break
                        #         if del_flag:
                        #             active_traffic_item.routes.remove(route)
                        #         else:
                        #             total_bandwidth += route_bandwidth



                    else:
                        # 年齢加算
                        link_item.add_age()
                        link_list2[(link_item_key[0], link_item_key[1])].add_age()
                        link_list3[(link_item_key[0], link_item_key[1])].add_age()
                        link_list4[(link_item_key[0], link_item_key[1])].add_age()
                        link_list5[(link_item_key[0], link_item_key[1])].add_age()
                        link_list6[(link_item_key[0], link_item_key[1])].add_age()

                else: # リンク故障しているとき
                    if fail_repair_info[link_item_key].failure_status == 0: # 0だったら故障が戻っているということ
                    # if cls.is_repaired(average_repaired_time, link_item.failure_status):
                        new_shape = link_item.shape
                        new_scale = link_item.scale
                        # 復旧(使用帯域幅解放は実行済み)
                        # リンク故障率再設定
                        cls.write_log("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_item.reset(new_shape, new_scale)
                        cls.write_log2("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list2[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log3("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list3[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log4("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list4[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log5("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list5[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                        cls.write_log6("[Link repaired] %d->%d\n" % (link_item_key[0], link_item_key[1]))
                        link_list6[(link_item_key[0], link_item_key[1])].reset(new_shape, new_scale)
                    else:
                        link_item.failure_status += 1
        
        cls.write_log_fail_rate("--Time [{}] Current link failure rate --\n".format(time))
        for link_item_key, link_item in link_list.items():
            cls.write_log_fail_rate("{}->{}, failure_rate: {}\n".format(link_item_key[0], link_item_key[1], link_item.failure_rate))
        cls.write_log_fail_rate("\n")
        return

    @classmethod
    def link_status(cls, link_list, average_repaired_time):
        # リンク障害判定
        for link_item_key, link_item in link_list.items():
            if link_item is not None:
                if link_item.failure_status == 0:  #リンク故障していない時
                    link_item.update_link_failure_rate()  #リンク故障率更新 
                    
                    if cls.is_failure(link_item.failure_rate):  #リンク故障判定
                        link_item.failure_status += 1
                        print("[Link failed] {} -> {}".format(link_item_key[0], link_item_key[1]))
                        cls.write_log_fail("[Link failed] {} -> {}\n".format(link_item_key[0], link_item_key[1]))
                    else:
                        link_item.add_age()  #年齢加算
                        
                else:  #リンク故障している時
                    if cls.is_repaired(average_repaired_time, link_item.failure_status):
                        new_shape = link_item.shape
                        new_scale = link_item.scale
                        # 復旧(使用帯域幅解放は実行済み)
                        # リンク故障率再設定
                        print("[Link repaired] {} -> {}".format(link_item_key[0], link_item_key[1]))
                        cls.write_log_fail("[Link repaired] {} -> {}\n".format(link_item_key[0], link_item_key[1]))
                        link_item.reset(new_shape, new_scale)
                    else:
                        link_item.failure_status += 1


