"测试集生成模块"
from Typing.TestSet import TestSet
from Typing.VLink import VLink
from Typing.Frame import Frame
from Typing.Task import Task
from Typing.Nodes import Node, NodeType

import networkx as nx
import time
import random
import math

# 全局测试参数输出文件
outputFile = open('param_output/param_{}.txt'.format(int(time.time())), "w")

def gen_vlink(mTestSet, dist_task_list, peroid_set):
    # 生成 Virtual Link
    # 先用迪杰斯特拉算法计算整个图的路由
    graph = mTestSet.graph
    shortest_path = nx.shortest_path(graph)
    
    # print('###### 测试虚链路生成 ######')
    vlid = 0
    while dist_task_list:
        '''
        # 每次产生两条，为解决剩余任务都在一个节点上的BUG
        # 每次选择两个端节点，对应任务集TaskList_1(3)和TaskList_2(4)
        # 在选出的两个任务集中再选择两个任务task_a(c)和task_b(d)
        '''
        TaskList_1 = random.choice(dist_task_list)
        # print(TaskList_1[3].nid)
        # 将已选端节点的集合移除避免重复选择端节点集合
        dist_task_list.remove(TaskList_1)
        TaskList_2 = random.choice(dist_task_list)
        dist_task_list.remove(TaskList_2)
        TaskList_3 = random.choice(dist_task_list)
        dist_task_list.remove(TaskList_3)
        TaskList_4 = random.choice(dist_task_list)
        dist_task_list.remove(TaskList_4)
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
                          mTestSet.linkSet, graph.nodeSet, False)
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
        mTestSet.addVLink(vlink_1)
        vlid += 1
        '''
        第二条虚拟链路
        '''
        peroid_2 = random.choice(peroidSet)
        # 设置相关任务的周期和截止时间
        task_c.T = task_c.D = peroid_2
        task_d.T = task_d.D = peroid_2
        vl_2 = gen_link_path(route, task_c, task_d,
                          mTestSet.linkSet, graph.nodeSet, False)

        vlink_2 = VLink(vlid, vl_2, peroid_2)
        vlink_2.setTaskPair(task_c, task_d)
        # 设置生产者任务和消费这任务的vlid和selfLink
        task_c.setVlid(vlid)
        task_d.setVlid(vlid)
        task_c.setSelfLink(vl_2[0])  # 生产者
        task_d.setSelfLink(vl_2[len(vl_2)-1])  # 消费者

        mTestSet.addVLink(vlink_2)
        vlid += 1
        '''
        注意将非空的集合放回
        '''
        # 将集合1重新放入，在其不为空时
        if TaskList_1:
            dist_task_list.append(TaskList_1)
        if TaskList_2:
            dist_task_list.append(TaskList_2)
        if TaskList_3:
            dist_task_list.append(TaskList_3)
        if TaskList_4:
            dist_task_list.append(TaskList_4)
        # print(dist_task_list)

    # 生成Free-task的selfLink以及对应的VLink
    for task in freeTaskList:
        task.setVlid(vlid)
        # 生成selfLink
        fperoid = random.choice(peroidSet)
        task.T = task.D = fperoid
        fvl = gen_link_path(route, task, task,
                         mTestSet.linkSet, graph.nodeSet, True)
        fvlink = VLink(vlid, fvl, fperoid)
        fvlink.setSelfLinkFlag()
        fvlink.setTaskPair(task, task)
        mTestSet.addVLink(fvlink)
        task.setSelfLink(fvl[0]) # 应该只有一个元素
        vlid += 1

    return True


def gen_wcet(mTestSet, utilization):
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
    nodeNum = mTestSet.nodeNum

    '''
    遍历free任务集，为每一个任务计算WCET
    '''
    for i in range(nodeNum):
        taskList = mTestSet.taskSet[i]
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
        taskList = mTestSet.taskSet[i]
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
        taskList = mTestSet.taskSet[i]
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
        taskList = mTestSet.taskSet[i]
        testUtil = 0
        for j in range(0, comu_task_num):
            if (taskList[j].C < 0):
                print('@@@@@@@@@@@@ ErroR in gen_wcet：执行时间为负')
            testUtil += taskList[j].C / taskList[j].T
        outputFile.write('端节点{0}上通信任务利用率：{1:.4f}\n'.format(i, testUtil))


def gen_vlink_and_task(mTestSet, peroid_set, utilization):
    '''
    在mtestSet中生成虚链路和测试任务集
    参数：
        mtestSet：测试集类，存储任务和虚链路
        peroidSet：预定义的周期集合，任务的周期在其中随机挑选
        utilization: 每个端节点上的利用率
    '''
    #node_num = mTestSet.node_num
    free_task_num = mTestSet.free_task_num # 无通讯任务个数，每端节点
    comm_task_num = mTestSet.comm_task_num  # 通信任务个数，每端节点
    all_task_num = free_task_num + comm_task_num
    graph = mTestSet.graph # 拓扑结构图

    # 每个节点：8 free-task, 8 communicating-task
    #vlink_num = comm_task_num * node_num // 2
    #selflink_num = all_task_num * node_num

    # 用于生成虚链路，存储每个节点上的通信任务集
    dist_task_list = []

    for node in graph.nodes:
        # 排除交换机
        if node.ntype == NodeType.ENDSYSTEM:
            continue
        # 把同个端节点上的任务放到一个列表里
        task_list = []
        print("### Node ID {}.\n".format(node.nid))
        # Comm Task Gens
        for i in range(0, comm_task_num):
            # tid高16为表示节点编号，低16位表示节点内任务编号
            _tid = (node.nid << 16) | i 
            _ttask = Task(tid=_tid)
            # 放入所有task的集合
            node.comm_task_list.append(_ttask)
            # 放入同一端节点的通信任务集合
            task_list.append(_ttask)
        # Free Task Gens
        for j in range(comm_task_num, all_task_num):
            # free-task 生成
            _tid = (node.nid << 16) | j
            _ftask = Task(tid=_tid)
            _peroid = random.choice(peroid_set)
            _ftask.T = _ftask.D = _peroid
            node.free_task_list.append(_ftask)
        # 所有列表组成一个大列表
        dist_task_list.append(task_list)

    # 初始化 TestSet的任务集
    # mTestSet.initTaskSet(all_task_list)

    # 生成虚链路
    gen_vlink(mTestSet, dist_task_list, peroid_set)

    # 根据利用率调整任务的wcet（task.C）
    gen_wcet(mTestSet, utilization)

    '''
    测试生成的任务集合和生成的虚拟链路集合
    '''
    outputFile.write('###### 生成的任务集合信息 ######\n')
    for i in range(nodeNum):
        outputFile.write('End System id {}:\n'.format(i))
        for j in range(allTaskNum):
            outputFile.write('task_{}_{}: C = {},\tT = D = {},\tvlid={},\tselfLink.name={}\n'.format(
                all_task_list[i][j].nid, all_task_list[i][j].tid, all_task_list[i][j].C,
                all_task_list[i][j].T, all_task_list[i][j].vlid, all_task_list[i][j].selfLink.name))
    outputFile.write('###### 生成的虚拟链路信息 ######\n')
    for i in range(vlinkNum):
        vlink = mTestSet.vlinkSet[i]
        outputFile.write('vlink id {}:\n'.format(vlink.vlid))
        # outputFile.write(mTestSet.vlinkSet[i].vl, end=', ')
        for link in vlink.vl:
            outputFile.write('{}.s = {}, '.format(link.name, link.speed_coefficient))
        outputFile.write('head = task_{}_{}, tail = task_{}_{}, '.format(
            vlink.task_p.nid, vlink.task_p.tid, vlink.task_c.nid, vlink.task_c.tid))
        outputFile.write('max_latency = {}.\n'.format(mTestSet.vlinkSet[i].max_latency))

    return True


def gen_frame_set(mTestSet):
    '''
        结构：字典: vlink id --> sub dictionary
        子字典：link id(在虚链路中的编号) --> Frame_list
    '''
    frameSet = mTestSet.frameSet
    for i in range(len(mTestSet.vlinkSet)):
        mvl = mTestSet.vlinkSet[i]
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
        message = mTestSet.messageSet[i]  # 消息
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
    for task in mTestSet.taskFrameSet:
        task_frame_list = mTestSet.taskFrameSet[task]
        outputFile.write('Task_{}_{}:\n'.format(task.nid, task.tid))
        for frame in task_frame_list:
            outputFile.write('\tFrame_({})_{}_{}\t: T = {},\tL = {}\n'.format(
                    frame.lname[0]+'_'+frame.lname[1], frame.vlid, frame.fid, frame.T, frame.L))


def gen_testSet(mTestSet, peroidSet, utilization, granuolarity):
    '''
    功能描述：
        生成测试集
    参数描述：
        mTestSet: 测试集类
        peroidSet: 任务周期集合
        utilization: 任务集总体利用率
        granuolarity: 任务调度时间粒度，单位：微秒
    '''
    #
    print('测试参数生成在{}文件'.format(outputFile.name))

    outputFile.write('###### 拓扑图初始化信息 ######\n')

    # init virtual link set and task set
    gen_vlink_and_task(mTestSet, peroidSet, utilization)

    # init message set (static)

    for i in range(len(mTestSet.vlinkSet)):
        mvl = mTestSet.vlinkSet[i]
        if mvl.isSelfLink:
            continue
        vlid = mvl.vlid
        T = mvl.max_latency
        size = random.randint(84, 1542)
        mmessage = Message(vlid, T, size)
        # 添加到测试类中
        mTestSet.addMessage(mmessage)

    outputFile.write('###### Message集合初始化信息 ######\n')
    for mm in mTestSet.messageSet:
        outputFile.write('Message_{}:\tT = {}, L = {}\n'.format(mm.vlid, mm.peroid, mm.size))

    # init Frame set (static)
    gen_frame_set(mTestSet)

    #close file
    outputFile.close()


__version__ = '2.0'
