from TestSet import TestSet
from Task import Task
from Graph import Graph
from VLink import VLink
from Message import Message
from Frame import Frame
from Link import Link

import random
import math
import pdb


def find_path(graph, src):
    '''
    采用迪杰斯特拉算法简单的生成整个网络拓扑的路由
    目前不考虑负载均衡
    '''
    if graph is None:
        return None

    # 生成到达矩阵
    links = graph.linkSet  # 图中所有的链路
    nodestrings = graph.nodeSet  # 图中所有的节点
    nodes = [i for i in range(len(nodestrings))]
    gList = [[float('inf') for col in range(len(nodes))]
             for row in range(len(nodes))]
    for link in links:
        node_a = link[0]
        node_b = link[1]
        index_a = nodestrings.index(node_a)
        index_b = nodestrings.index(node_b)
        gList[index_a][index_b] = 1
    for i in range(len(nodes)):
        gList[i][i] = 0
    # print(gList)
    visited = []  # 表示已经路由到最短路径的节点集合

    if src in nodes:
        visited.append(src)
        nodes.remove(src)
    else:
        return None

    distance = {src: 0}  # 记录源节点到各个节点的距离
    for i in nodes:
        distance[i] = gList[src][i]
    # print(distance)
    path = {src: {src: []}}  # 记录源节点到每个节点的路径
    k = pre = src
    while nodes:
        mid_distance = float('inf')
        for v in visited:
            for d in nodes:
                new_distance = gList[src][v] + gList[v][d]
                if new_distance < mid_distance:
                    mid_distance = new_distance
                    gList[src][d] = new_distance  # 更新距离
                    k = d
                    pre = v

        distance[k] = mid_distance  # 最短路径
        path[src][k] = [i for i in path[src][pre]]
        path[src][k].append(k)
        # 更新两个节点集合
        visited.append(k)
        nodes.remove(k)
        # print(visited, nodes)  # 输出
    # return path, distance
    return path


def find_link(linkSet, node_1, node_2):
    '''
    返回linkSet中node_1与node_2之间的链路，无方向
    找到返回Link，否则返回None
    '''
    key = '{}_{}'.format(node_1, node_2)
    if key in linkSet:
        return linkSet[key]
    key = '{}_{}'.format(node_2, node_1)
    if key in linkSet:
        return linkSet[key]
    return None


def gen_a_link(route, task_p, task_c, linkSet, nodeSet):

    # 设置VLink path, exmaple:['t_0_1', 'v0', 's0', 's1', 'v3', 't_3_6']
    # 添加头: self link
    vl = []
    vl_ele_head = nodeSet[task_p.nid]
    link = find_link(linkSet, vl_ele_head, vl_ele_head)
    vl.append(link)
    # 从计算好的路由中取出最短路径
    path = route[task_p.nid][task_c.nid]
    # 添加到VLink中
    for node in path:
        vl_ele_tail = nodeSet[node]
        link = find_link(linkSet, vl_ele_head, vl_ele_tail)
        vl.append(link)
        # 设置下一个头
        vl_ele_head = nodeSet[node]
    # 添加尾： self link
    vl_ele_tail = vl_ele_head
    link = find_link(linkSet, vl_ele_head, vl_ele_tail)
    vl.append(link)

    return vl


def gen_vlink(mtestSet, distTaskList, peroidSet):
    # 生成 Virtual Link
    # 先用迪杰斯特拉算法计算整个图的路由
    route = {}
    for i in range(len(mtestSet.graph.nodeSet)):
        path = find_path(mtestSet.graph, i)
        #print(distance, path)
        route[i] = path[i]
    # print(route)
    # print('###### 测试虚链路生成 ######')
    vlid = 0
    while distTaskList:
        '''
        # 每次产生两条，为解决剩余任务都在一个节点上的BUG
        # 每次选择两个端节点，对应任务集TaskList_1(3)和TaskList_2(4)
        # 在选出的两个任务集中再选择两个任务task_a(c)和task_b(d)
        '''
        TaskList_1 = random.choice(distTaskList)
        # print(TaskList_1[3].nid)
        # 将已选端节点的集合移除避免重复选择端节点集合
        distTaskList.remove(TaskList_1)
        TaskList_2 = random.choice(distTaskList)
        distTaskList.remove(TaskList_2)
        TaskList_3 = random.choice(distTaskList)
        distTaskList.remove(TaskList_3)
        TaskList_4 = random.choice(distTaskList)
        distTaskList.remove(TaskList_4)
        # print(TaskList_2[3].nid)
        # 选择并移除随机的两个任务
        task_a = random.choice(TaskList_1)
        TaskList_1.remove(task_a)
        task_b = random.choice(TaskList_2)
        TaskList_2.remove(task_b)
        task_c = random.choice(TaskList_3)
        TaskList_3.remove(task_c)
        task_d = random.choice(TaskList_4)
        TaskList_4.remove(task_d)
        '''
        第一条虚拟链路
        '''
        # 从周期集合中随机选择一个周期
        peroid_1 = random.choice(peroidSet)
        # 设置相关任务的周期和截止时间
        task_a.T = task_a.D = peroid_1
        task_b.T = task_b.D = peroid_1

        vl_1 = gen_a_link(route, task_a, task_b,
                          mtestSet.linkSet, mtestSet.graph.nodeSet)
        # 初始化VLink类
        vlink_1 = VLink(vlid, vl_1, peroid_1)
        # 添加生产者任务和消费者任务
        vlink_1.setTaskPair(task_a, task_b)
        # 添加到测试集类中
        mtestSet.addVLink(vlink_1)
        vlid += 1
        '''
        第二条虚拟链路
        '''
        peroid_2 = random.choice(peroidSet)
        # 设置相关任务的周期和截止时间
        task_c.T = task_c.D = peroid_2
        task_d.T = task_d.D = peroid_2
        vl_2 = gen_a_link(route, task_c, task_d,
                          mtestSet.linkSet, mtestSet.graph.nodeSet)

        vlink_2 = VLink(vlid, vl_2, peroid_2)
        vlink_2.setTaskPair(task_c, task_d)
        mtestSet.addVLink(vlink_2)
        vlid += 1
        '''
        注意将非空的集合放回
        '''
        # 将集合1重新放入，在其不为空时
        if TaskList_1:
            distTaskList.append(TaskList_1)
        if TaskList_2:
            distTaskList.append(TaskList_2)
        if TaskList_3:
            distTaskList.append(TaskList_3)
        if TaskList_4:
            distTaskList.append(TaskList_4)
        # print(distTaskList)

    return True


'''
def gen_vlink_for_free(mtestSet, taskSet, peroidSet):

    vlid = len(mtestSet.vlinkSet)

    for task in taskSet:
        node = mtestSet.nodeSet[taks.nid]
        #vlink = VLink(vlid, )
'''


def gen_wcet(mtestSet, utilization):
    '''
    根据任务的利用率调整任务的WCET
    参数：
        mtestSet：测试集类，包含所有测试任务
        utilization: 每个端节点上的利用率
    '''
    # 常量定义
    free_task_ratio = 0.75  # free任务利用率占端节点利用率的比重
    all_task_num = 4  # 每个端节点任务的个数
    comu_task_num = 2  # 每个端节点的通信任务的个数

    free_task_util = free_task_ratio * utilization  # free任务的利用率
    comu_task_util = utilization - free_task_util  # 通信任务的利用率
    nodeNum = mtestSet.nodeNum

    '''
    遍历free任务集，为每一个任务计算WCET
    '''
    for i in range(nodeNum):
        taskList = mtestSet.taskSet[i]
        rest_util = free_task_util
        task_index = comu_task_num
        while task_index < all_task_num - 1:
            # 随机范围随着剩余利用率和任务id变化，任务id用于防止任务利用率单调减小
            myutil = random.uniform(
                rest_util * 0.2 * task_index / 10, rest_util * 0.45 * task_index / 10)
            # print('###临时测试 task_{}_{} 利用率为：{}'.format(i,task_index,myutil))
            taskList[task_index].C = int(myutil * taskList[task_index].T)
            rest_util -= myutil
            task_index += 1

        taskList[task_index].C = int(rest_util * taskList[task_index].T)
        # print('###临时测试 task_{}_{} 利用率为：{}'.format(i,task_index,rest_util))

    '''
    遍历通信任务集，为每一个任务计算WCET
    '''
    for i in range(nodeNum):
        taskList = mtestSet.taskSet[i]
        rest_util = comu_task_util
        task_index = 0
        while task_index < comu_task_num - 1:
            # 随机范围随着剩余利用率和任务id变化，任务id用于防止任务利用率单调减小
            myutil = random.uniform(
                rest_util * 0.2 * (task_index + 8) / 10, rest_util * 0.45 * (task_index + 8) / 10)
            # print('###临时测试 task_{}_{} 利用率为：{}'.format(i,task_index,myutil))
            taskList[task_index].C = int(myutil * taskList[task_index].T)
            rest_util -= myutil
            task_index += 1

        taskList[task_index].C = int(rest_util * taskList[task_index].T)
        # print('###临时测试 task_{}_{} 利用率为：{}'.format(i,task_index,rest_util))

    print('###### 验证端节点的利用率 ######')
    '''
    验证free任务的总利用为 0.75 * utilization
    '''
    for i in range(nodeNum):
        taskList = mtestSet.taskSet[i]
        testUtil = 0
        for j in range(comu_task_num, all_task_num):
            if (taskList[j].C < 0):
                print('@@@@@@@@@@@@ ErroR in gen_wcet：执行时间为负')
            testUtil += taskList[j].C / taskList[j].T
        print('端节点{}上free任务利用率：{}'.format(i, testUtil))

    '''
    验证通信任务的总利用为 0.25 * utilization
    '''
    for i in range(nodeNum):
        taskList = mtestSet.taskSet[i]
        testUtil = 0
        for j in range(0, comu_task_num):
            if (taskList[j].C < 0):
                print('@@@@@@@@@@@@ ErroR in gen_wcet：执行时间为负')
            testUtil += taskList[j].C / taskList[j].T
        print('端节点{}上通信任务利用率：{}'.format(i, testUtil))


def gen_vl_and_task(mtestSet, peroidSet, utilization):
    '''
    在mtestSet中生成虚链路和测试任务集
    参数：
        mtestSet：测试集类，存储任务和虚链路
        peroidSet：预定义的周期集合，任务的周期在其中随机挑选
        utilization: 每个端节点上的利用率
    '''
    nodeNum = mtestSet.nodeNum

    # 常量定义
    vlinkNum = int(2 * nodeNum / 2)  # 每个节点：8 free-task, 8 communicating-task
    allTaskNum = 4
    communTaskNum = 2  # 通信任务个数，每个端节点上
    # 存储每个节点上任务集合的字典
    allTaskList = {}
    # 用于生成虚链路，存储每个节点上的通信任务集
    distTaskList = []
    for i in range(0, nodeNum):
        # 把同个端节点上的任务放到一个列表里
        taskList = []
        allTaskList[i] = []
        for j in range(0, communTaskNum):
            ttask = Task(i, j)
            # 放入所有task的集合
            allTaskList[i].append(ttask)
            # 放入同一端节点的通信任务集合
            taskList.append(ttask)
        for j in range(communTaskNum, allTaskNum):
            # free-task 生成
            ttask = Task(i, j)
            peroid = random.choice(peroidSet)
            ttask.T = ttask.D = peroid
            allTaskList[i].append(ttask)
        # 所有列表组成一个大列表
        distTaskList.append(taskList)

    # 初始化 TestSet的任务集
    mtestSet.initTaskSet(allTaskList)

    # 生成虚链路
    gen_vlink(mtestSet, distTaskList, peroidSet)

    # 根据利用率调整任务的wcet（task.C）
    gen_wcet(mtestSet, utilization)

    '''
    测试生成的任务集合和生成的虚拟链路集合
    '''
    print('###### 生成的任务集合信息 ######')
    for i in range(nodeNum):
        print('End System id {}:'.format(i))
        for j in range(allTaskNum):
            print('task_{}_{}:\tC = {}, T = D = {}'.format(
                allTaskList[i][j].nid, allTaskList[i][j].tid, allTaskList[i][j].C, allTaskList[i][j].T))
    print('###### 生成的虚拟链路信息 ######')
    for i in range(vlinkNum):
        vlink = mtestSet.vlinkSet[i]
        print('vlink id {}:'.format(vlink.vlid))
        # print(mtestSet.vlinkSet[i].vl, end=', ')
        for link in vlink.vl:
            print('{}.s = {}'.format(link.name, link.speed_coefficient), end=', ')
        print('head = task_{}_{}, tail = task_{}_{}'.format(
            vlink.task_p.nid, vlink.task_p.tid, vlink.task_c.nid, vlink.task_c.tid), end=', ')
        print('max_latency = {}.'.format(mtestSet.vlinkSet[i].max_latency))

    return True


def gen_frame_set(mtestSet, granuolarity):
    '''
        结构：字典: vlink id --> sub dictionary
        子字典：link id(在虚链路中的编号) --> Frame_list
    '''
    for i in range(len(mtestSet.vlinkSet)):
        mvl = mtestSet.vlinkSet[i]
        vlid = mvl.vlid
        message = mtestSet.messageSet[i]  # 消息
        mtestSet.frameSet[i] = {}
        fid = 0
        # 生产者任务的Frame生成
        task = mvl.task_p
        link = mvl.vl[0]
        mtestSet.frameSet[i][link] = []
        frame_list = mtestSet.frameSet[i][link]
        for j in range(math.ceil(task.C / granuolarity)):
            frame = Frame(vlid, fid, link.name)
            frame.setPeroid(int(task.T / granuolarity))
            frame.setDuration(1)  # CPU Line Frame.L = 1 macrotick
            frame_list.append(frame)
            fid += 1
        # 消息的Frame生成
        for j in range(1, len(mvl.vl) - 1):
            link = mvl.vl[j]  # 物理链路
            mtestSet.frameSet[i][link] = []
            frame_list = mtestSet.frameSet[i][link]
            mframe = Frame(vlid, fid, link.name)
            mframe.setPeroid(math.ceil(message.peroid / link.macrotick))
            mframe.setDuration(
                math.ceil(message.size * link.speed_coefficient / link.macrotick))
            frame_list.append(mframe)
            fid += 1
        # 消费者的Frame生成
        task = mvl.task_c
        link = mvl.vl[len(mvl.vl) - 1]
        mtestSet.frameSet[i][link] = []
        frame_list = mtestSet.frameSet[i][link]
        for j in range(math.ceil(task.C / granuolarity)):
            frame = Frame(vlid, fid, link.name)
            frame.setPeroid(int(task.T / granuolarity))
            frame.setDuration(1)  # CPU Line Frame.L = 1 macrotick
            frame_list.append(frame)
            fid += 1
    '''
    # 生成free-task的Frame
    for i in range(len(mtestSet.taskSet)):
        tasklist = mtestSet.taskSet[i]
        vlid = len(mtestSet.frameSet)
        for task in tasklist:
            # 排除通信任务
            if task.tid < 8:
                continue
            fid = 0
            mtestSet.frameSet[vlid] = []
            for j in range(math.ceil(task.C / granuolarity)):
                frame = Frame( vlid , fid) # self link -1
                frame.setPeroid(int(task.T / granuolarity))
                frame.setDuration(1)  # CPU Line Frame.L = 1 macrotick
                mtestSet.frameSet[vlid].append(frame)
                fid += 1
            vlid += 1
    '''
    # pdb.set_trace()
    all_frame_set = mtestSet.frameSet
    # 生成frameSet，第一层以Link检索，第二层以Vlink检索
    all_frame_sorted_by_link = mtestSet.frameSetSortByLink
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for link in vl_frame_list:
            frame_list = vl_frame_list[link]
            for frame in frame_list:
                # 对于每一个frame放入对应的位置
                # 如果link索引为空，新建子字典
                if not (link in all_frame_sorted_by_link):
                    all_frame_sorted_by_link[link] = {}
                # 如果vlid_t子索引为空，新建列表
                if not (vlid_t in all_frame_sorted_by_link[link]):
                    all_frame_sorted_by_link[link][vlid_t] = []
                # 添加Frame
                #print('##link:{}, vlid_t:{}, frameid:{}'.format(link.name, vlid_t, frame.fid))
                all_frame_sorted_by_link[link][vlid_t].append(frame)
                #print(all_frame_sorted_by_link[link][vlid_t])
                # OK


    '''
    测试Frame集合
    '''

    print('###### Frame集合初始化信息(VLink版本) ######')
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for link in vl_frame_list:
            frame_list = vl_frame_list[link]
            for frame in frame_list:
                print('Frame_{}_{}_{}:\t\tT = {}, L = {}'.format(
                    frame.vlid, frame.lname, frame.fid, frame.T, frame.L))

    print('###### Frame集合初始化信息(Link版本) ######')
    # print(all_frame_sorted_by_link)
    for link in all_frame_sorted_by_link:
        link_frame_list = all_frame_sorted_by_link[link]
        for vlid_t in link_frame_list:
            frame_list = link_frame_list[vlid_t]
            for frame in frame_list:
                print('Frame_{}_{}_{}:\t\tT = {}, L = {}'.format(
                    frame.lname, frame.vlid, frame.fid, frame.T, frame.L))


def generate(mtestSet, peroidSet, utilization, granuolarity):
    nodeNum = mtestSet.nodeNum
    switchNum = mtestSet.switchNum
    # init node set
    nodeSet = []
    for i in range(0, nodeNum):
        nodeSet.append('v{0}'.format(i))
    for i in range(0, switchNum):
        nodeSet.append('s{0}'.format(i))

    # init link set
    tlinkSet = {}  # testSet中的linkset,包括selflink和无向的物理link
    linkSet = []  # 拓扑图中的linkset, 双向物理link
    for i in range(0, int(nodeNum / 2)):
        linkSet.append(['v{0}'.format(i), 's0'])
        linkSet.append(['s0', 'v{0}'.format(i)])
        # setup tlinkSet
        vl_ele_head = 'v{}'.format(i)
        vl_ele_tail = 's0'
        vl_element = [vl_ele_head, vl_ele_tail]
        speed = 0.08  # 100Mbit/s 链路传输一个字节需要的时间
        link = Link(vl_element, speed, 5)  # FIXME delay
        tlinkSet['{}_{}'.format(vl_ele_head, vl_ele_tail)] = link
    for i in range(int(nodeNum / 2), nodeNum):
        linkSet.append(['v{0}'.format(i), 's1'])
        linkSet.append(['s1', 'v{0}'.format(i)])
        # setup tlinkSet
        vl_ele_head = 'v{}'.format(i)
        vl_ele_tail = 's1'
        vl_element = [vl_ele_head, vl_ele_tail]
        speed = 0.08  # 100Mbit/s 链路传输一个字节需要的时间
        link = Link(vl_element, speed, 5)  # FIXME delay
        tlinkSet['{}_{}'.format(vl_ele_head, vl_ele_tail)] = link
    # 交换机之间
    linkSet.append(['s0', 's1'])
    linkSet.append(['s1', 's0'])
    # tlinkSet
    vl_element = ['s0', 's1']
    speed = 0.008  # 1Gbit/s
    link = Link(vl_element, speed, 5)
    tlinkSet['s0_s1'] = link
    # tlinkSet selflink
    for i in range(0, nodeNum):
        vl_element = ['v{}'.format(i), 'v{}'.format(i)]
        speed = 0  # 暂时不用
        link = Link(vl_element, speed, 250)  # FIXME delay
        tlinkSet['v{0}_v{0}'.format(i)] = link

    print('###### 拓扑图初始化信息 ######')
    print('LinkSet = {}'.format(linkSet))
    print('NodeSet = {}'.format(nodeSet))

    # init graph
    mtestSet.initGraph(linkSet, nodeSet)
    # init test link set (包括selflink 和 无向的物理link)
    mtestSet.initLinkSet(tlinkSet)

    # init virtual link set and task set
    gen_vl_and_task(mtestSet, peroidSet, utilization)

    # init message set (static)

    for i in range(len(mtestSet.vlinkSet)):
        mvl = mtestSet.vlinkSet[i]
        vlid = mvl.vlid
        T = mvl.max_latency
        size = random.randint(84, 1542)
        mmessage = Message(vlid, T, size)
        # 添加到测试类中
        mtestSet.addMessage(mmessage)

    print('###### Message集合初始化信息 ######')
    for mm in mtestSet.messageSet:
        print('Message_{}:\tT = {}, L = {}'.format(mm.vlid, mm.peroid, mm.size))

    # init Frame set (static)
    gen_frame_set(mtestSet, granuolarity)


__version__ = '0.5'
