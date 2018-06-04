#/usr/bin/env python
"测试集生成模块"

from Typing.TestSet import TestSet
from Typing.Task import Task
from Typing.Graph import Graph
from Typing.VLink import VLink
from Typing.Message import Message
from Typing.Frame import Frame
from Typing.Link import Link

import time
import random
import math
import pdb

# 全局测试参数输出文件
outputFile = open('param_output/param_{}.txt'.format(int(time.time())), "w")

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


def gen_link_path(route, task_p, task_c, linkSet, nodeSet, isSelfLink):
    '''
    设置VLink path, exmaple:['t_0_1', 'v0', 's0', 's1', 'v3', 't_3_6']
    '''
    # 添加头: self link
    vl = []
    vl_ele_head = nodeSet[task_p.nid]
    link = find_link(linkSet, vl_ele_head, vl_ele_head)
    vl.append(link)
    if isSelfLink:
        return vl
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


def gen_vlink(mtestSet, distTaskList, freeTaskList, peroidSet):
    # 生成 Virtual Link
    # 先用迪杰斯特拉算法计算整个图的路由
    route = {}
    graph = mtestSet.graph
    for i in range(len(graph.nodeSet)):
        path = graph.find_path(i)
        #print(path)
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

        vl_1 = gen_link_path(route, task_a, task_b,
                          mtestSet.linkSet, graph.nodeSet, False)
        # 初始化VLink类
        vlink_1 = VLink(vlid, vl_1, peroid_1)
        # 添加生产者任务和消费者任务
        vlink_1.setTaskPair(task_a, task_b)
        # 设置生产者任务和消费这任务的vlid和selfLink
        task_a.setVlid(vlid)
        task_b.setVlid(vlid)
        task_a.setSelfLink(vl_1[0])  # 生产者
        task_b.setSelfLink(vl_1[len(vl_1)-1])  # 消费者
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
        vl_2 = gen_link_path(route, task_c, task_d,
                          mtestSet.linkSet, graph.nodeSet, False)

        vlink_2 = VLink(vlid, vl_2, peroid_2)
        vlink_2.setTaskPair(task_c, task_d)
        # 设置生产者任务和消费这任务的vlid和selfLink
        task_c.setVlid(vlid)
        task_d.setVlid(vlid)
        task_c.setSelfLink(vl_2[0])  # 生产者
        task_d.setSelfLink(vl_2[len(vl_2)-1])  # 消费者

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

    # 生成Free-task的selfLink以及对应的VLink
    for task in freeTaskList:
        task.setVlid(vlid)
        # 生成selfLink
        fperoid = random.choice(peroidSet)
        task.T = task.D = fperoid
        fvl = gen_link_path(route, task, task,
                         mtestSet.linkSet, graph.nodeSet, True)
        fvlink = VLink(vlid, fvl, fperoid)
        fvlink.setSelfLinkFlag()
        fvlink.setTaskPair(task, task)
        mtestSet.addVLink(fvlink)
        task.setSelfLink(fvl[0]) # 应该只有一个元素
        vlid += 1

    return True


def gen_wcet(mtestSet, utilization):
    '''
    根据任务的利用率调整任务的WCET
    参数：
        mtestSet：测试集类，包含所有测试任务
        utilization: 每个端节点上的利用率
    '''
    # 常量定义
    free_task_ratio = 0.75  # free任务利用率占端节点利用率的比重
    all_task_num = 16  # 每个端节点任务的个数
    comu_task_num = 8  # 每个端节点的通信任务的个数

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

    outputFile.write('###### 验证端节点的利用率 ######\n')
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
        outputFile.write('端节点{0}上free任务利用率：{1:.4f}\n'.format(i, testUtil))

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
        outputFile.write('端节点{0}上通信任务利用率：{1:.4f}\n'.format(i, testUtil))


def gen_vlink_and_task(mtestSet, peroidSet, utilization):
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
    allTaskNum = 16
    communTaskNum = 8  # 通信任务个数，每个端节点上
    # 存储每个节点上任务集合的字典
    allTaskList = {}
    # 用于生成虚链路，存储每个节点上的通信任务集
    distTaskList = []
    # free task list
    freeTaskList = []
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
            freeTaskList.append(ttask)
            allTaskList[i].append(ttask)
        # 所有列表组成一个大列表
        distTaskList.append(taskList)

    # 初始化 TestSet的任务集
    mtestSet.initTaskSet(allTaskList)

    # 生成虚链路
    gen_vlink(mtestSet, distTaskList, freeTaskList, peroidSet)

    # 根据利用率调整任务的wcet（task.C）
    gen_wcet(mtestSet, utilization)

    '''
    测试生成的任务集合和生成的虚拟链路集合
    '''
    outputFile.write('###### 生成的任务集合信息 ######\n')
    for i in range(nodeNum):
        outputFile.write('End System id {}:\n'.format(i))
        for j in range(allTaskNum):
            outputFile.write('task_{}_{}: C = {},\tT = D = {},\tvlid={},\tselfLink.name={}\n'.format(
                allTaskList[i][j].nid, allTaskList[i][j].tid, allTaskList[i][j].C,
                allTaskList[i][j].T, allTaskList[i][j].vlid, allTaskList[i][j].selfLink.name))
    outputFile.write('###### 生成的虚拟链路信息 ######\n')
    for i in range(vlinkNum):
        vlink = mtestSet.vlinkSet[i]
        outputFile.write('vlink id {}:\n'.format(vlink.vlid))
        # outputFile.write(mtestSet.vlinkSet[i].vl, end=', ')
        for link in vlink.vl:
            outputFile.write('{}.s = {}, '.format(link.name, link.speed_coefficient))
        outputFile.write('head = task_{}_{}, tail = task_{}_{}, '.format(
            vlink.task_p.nid, vlink.task_p.tid, vlink.task_c.nid, vlink.task_c.tid))
        outputFile.write('max_latency = {}.\n'.format(mtestSet.vlinkSet[i].max_latency))

    return True


def gen_frame_set(mtestSet):
    '''
        结构：字典: vlink id --> sub dictionary
        子字典：link id(在虚链路中的编号) --> Frame_list
    '''
    frameSet = mtestSet.frameSet
    for i in range(len(mtestSet.vlinkSet)):
        mvl = mtestSet.vlinkSet[i]
        vlid = mvl.vlid
        fid = 0
        # 生产者任务的Frame生成
        task = mvl.task_p
        link = mvl.vl[0]
        for j in range(math.ceil(task.C / link.macrotick / 1)):
            frame = Frame(vlid, fid, link.name)
            frame.setPeroid(int(task.T / link.macrotick))
            frame.setDuration(1)  # CPU Line Frame.L = 2 macrotick
            # add to frameSet
            frameSet.addVlinkLinkIndex(i, link, frame)
            frameSet.addTaskIndex(task, frame)
            fid += 1
        # 如果只是selflink，跳过后续的步骤
        if mvl.isSelfLink:
            continue
        # 消息的Frame生成
        message = mtestSet.messageSet[i]  # 消息
        for j in range(1, len(mvl.vl) - 1):
            link = mvl.vl[j]  # 物理链路
            mframe = Frame(vlid, fid, link.name)
            mframe.setPeroid(math.ceil(message.peroid / link.macrotick))
            mframe.setDuration(
                math.ceil(message.size * link.speed_coefficient / link.macrotick))
            # add to frameSet
            frameSet.addVlinkLinkIndex(i, link, mframe)
            frameSet.addMessageIndex(message, mframe)
            fid += 1
        # 消费者的Frame生成
        task = mvl.task_c
        link = mvl.vl[len(mvl.vl) - 1]
        for j in range(math.ceil(task.C / link.macrotick / 1)):
            frame = Frame(vlid, fid, link.name)
            frame.setPeroid(int(task.T / link.macrotick))
            frame.setDuration(1)  # CPU Line Frame.L = 2 macrotick
            # add to frameSet
            frameSet.addVlinkLinkIndex(i, link, frame)
            frameSet.addTaskIndex(task, frame)
            fid += 1
    
    # 生成frameSet，第一层以Link检索，第二层以Vlink检索
    for vlid in frameSet.vlldict:
        framedict = frameSet.vlldict[vlid]
        for link in framedict:
            framelist = framedict[link]
            for frame in framelist: 
                # 添加Frame
                # outputFile.write('##link:{}, vlid_t:{}, frameid:{}'.format(link.name, vlid_t, frame.fid))
                frameSet.addLinkVlinkIndex(vlid, link, frame)
                # outputFile.write(all_frame_sorted_by_link[link][vlid_t])
                # OK

    '''
    测试Frame集合
    '''
    outputFile.write('###### Frame集合初始化信息(VLink版本) ######\n')
    for vlid_t in frameSet.vlldict:
        vl_frame_list = frameSet.vlldict[vlid_t]
        for link in vl_frame_list:
            frame_list = vl_frame_list[link]
            for frame in frame_list:
                outputFile.write('Frame_{}_({})_{}\t: T = {},\tL = {}\n'.format(
                    frame.vlid, frame.lname[0]+'_'+frame.lname[1], frame.fid, frame.T, frame.L))

    outputFile.write('###### Frame集合初始化信息(Link版本) ######\n')
    # outputFile.write(all_frame_sorted_by_link)
    for link in frameSet.lvldict:
        link_frame_list = frameSet.lvldict[link]
        for vlid_t in link_frame_list:
            frame_list = link_frame_list[vlid_t]
            for frame in frame_list:
                outputFile.write('Frame_({})_{}_{}\t: T = {},\tL = {}\n'.format(
                    frame.lname[0]+'_'+frame.lname[1], frame.vlid, frame.fid, frame.T, frame.L))
    outputFile.write('###### Frame集合初始化信息(Task版本) ######\n')
    for task in mtestSet.taskFrameSet:
        task_frame_list = mtestSet.taskFrameSet[task]
        outputFile.write('Task_{}_{}:\n'.format(task.nid, task.tid))
        for frame in task_frame_list:
            outputFile.write('\tFrame_({})_{}_{}\t: T = {},\tL = {}\n'.format(
                    frame.lname[0]+'_'+frame.lname[1], frame.vlid, frame.fid, frame.T, frame.L))


def generate(mtestSet, peroidSet, utilization, granuolarity):
    nodeNum = mtestSet.nodeNum
    switchNum = mtestSet.switchNum

    #
    print('测试参数生成在{}文件'.format(outputFile.name))
    
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
        link = Link(vl_element, speed, 10, 1)  # FIXME delay
        tlinkSet['{}_{}'.format(vl_ele_head, vl_ele_tail)] = link
    for i in range(int(nodeNum / 2), nodeNum):
        linkSet.append(['v{0}'.format(i), 's1'])
        linkSet.append(['s1', 'v{0}'.format(i)])
        # setup tlinkSet
        vl_ele_head = 'v{}'.format(i)
        vl_ele_tail = 's1'
        vl_element = [vl_ele_head, vl_ele_tail]
        speed = 0.08  # 100Mbit/s 链路传输一个字节需要的时间
        link = Link(vl_element, speed, 10, 1)  # FIXME delay
        tlinkSet['{}_{}'.format(vl_ele_head, vl_ele_tail)] = link
    # 交换机之间
    linkSet.append(['s0', 's1'])
    linkSet.append(['s1', 's0'])
    # tlinkSet
    vl_element = ['s0', 's1']
    speed = 0.008  # 1Gbit/s
    link = Link(vl_element, speed, 10, 1)
    tlinkSet['s0_s1'] = link
    # tlinkSet selflink
    for i in range(0, nodeNum):
        vl_element = ['v{}'.format(i), 'v{}'.format(i)]
        speed = 0  # 暂时不用
        link = Link(vl_element, speed, 250, 250)  # FIXME delay
        tlinkSet['v{0}_v{0}'.format(i)] = link

    outputFile.write('###### 拓扑图初始化信息 ######\n')
    outputFile.write('LinkSet = {}\n'.format(linkSet))
    outputFile.write('NodeSet = {}\n'.format(nodeSet))

    # init graph
    mtestSet.initGraph(linkSet, nodeSet)
    # init test link set (包括selflink 和 无向的物理link)
    mtestSet.initLinkSet(tlinkSet)

    # init virtual link set and task set
    gen_vlink_and_task(mtestSet, peroidSet, utilization)

    # init message set (static)

    for i in range(len(mtestSet.vlinkSet)):
        mvl = mtestSet.vlinkSet[i]
        if mvl.isSelfLink:
            continue
        vlid = mvl.vlid
        T = mvl.max_latency
        size = random.randint(84, 1542)
        mmessage = Message(vlid, T, size)
        # 添加到测试类中
        mtestSet.addMessage(mmessage)

    outputFile.write('###### Message集合初始化信息 ######\n')
    for mm in mtestSet.messageSet:
        outputFile.write('Message_{}:\tT = {}, L = {}\n'.format(mm.vlid, mm.peroid, mm.size))

    # init Frame set (static)
    gen_frame_set(mtestSet)

    #close file
    outputFile.close()


__version__ = '1.1'
