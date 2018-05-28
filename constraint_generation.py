#/usr/bin/env python
"约束生成模块"

from pysmt.shortcuts import Symbol, Or, GE, LT, Int, LE, And, GT
from pysmt.shortcuts import Plus, Times, Minus, Div
from pysmt.shortcuts import Solver, is_sat
from pysmt.logics import QF_LIA
from pysmt.typing import INT

import math
import pdb
import time


def frame_constraints(constraints, frameSet):
    '''0000000000000000
    向求解器中添加帧约束
        solver: z3求解器实例
        frameSet: 帧集合
    已验证:
        数值上，消息帧的大小会不会设置的不合理？
        目前只是一个包的随机大小（不超过一个包）
    '''
    # all_frame_set = testSet.frameSet
    for vlid_t in frameSet:
        vl_frame_list = frameSet[vlid_t]
        for link in vl_frame_list:
            framelist = vl_frame_list[link]
            for frame in framelist:
                #aCon = (frame.offset > 0, frame.offset < frame.T - frame.L)
                aCon = And(GT(frame.offset, Int(0)), 
                           LT(frame.offset, Int(frame.T-frame.L)))
                #print(aCon)
                constraints.append(aCon)

    # print(solver)
    # pdb.set_trace()
    return True


def lcm(ipt_a, ipt_b):
    '''
    求两个整数的最小公倍数
    已验证
    '''
    # 先求最大公约数
    a = ipt_a
    b = ipt_b
    while b != 0:
        c = a % b
        a = b
        b = c
    # 计算最小公倍数
    result = int(ipt_a * ipt_b / a)
    # print ('{} 和 {}的最小公倍数是{}'.format(ipt_a, ipt_b, result))
    return result


def link_constraints(constraints, frameSetSortedByLink):
    '''
    已验证
    '''
    # print ('###### 测试link constraints生成 ######')
    for link in frameSetSortedByLink:
        subFrameDict = frameSetSortedByLink[link]
        frameSameLink = []
        for vlid in subFrameDict:
            frameList = subFrameDict[vlid]
            for frame in frameList:
                frameSameLink.append(frame)
        # 对于同一个物理链路的任意两个帧成立：
        for i in range(len(frameSameLink)):
            for j in range(i+1, len(frameSameLink)):
                frame_i = frameSameLink[i]
                frame_j = frameSameLink[j]
                # 挑选不同虚链路的Frame
                if frame_i.vlid == frame_j.vlid:
                    continue
                # print('frame_i: {}_{}_{}, T={}, L={}, frame_j: {}_{}_{}, T={}, L={}'.format(
                #    frame_i.vlid, frame_i.lname, frame_i.fid, frame_i.T, frame_i.L,
                #    frame_j.vlid, frame_j.lname, frame_j.fid, frame_j.T, frame_j.L))
                hp = lcm(frame_i.T, frame_j.T)
                # 对于任意的阿尔法和贝塔属于....都满足：
                for alpha in range(int(hp / frame_i.T)):
                    for beta in range(int(hp / frame_j.T)):
                        # single_link_constraint = Or(
                        #    (frame_i.offset + alpha * frame_i.T >=
                        #     frame_j.offset + beta * frame_j.T + frame_j.L),
                        #    (frame_j.offset + beta * frame_j.T >= frame_i.offset + alpha * frame_i.T + frame_i.L))
                        single_link_constraint = Or(
                            GE(Plus(frame_i.offset, Int(alpha*frame_i.T)),
                               Plus(frame_j.offset, Int(beta*frame_j.T+frame_j.L))),
                            GE(Plus(frame_j.offset, Int(beta*frame_j.T)),
                               Plus(frame_i.offset, Int(alpha*frame_i.T+frame_i.L))))
                        #print('alpha={},beta={}:\nconstraint={}'.format(
                        #      alpha, beta, single_link_constraint))
                        constraints.append(single_link_constraint)
                # print(solver)
    # print(solver.check())
    # print(solver.model())
    # pdb.set_trace()
    # FIXME:提高效率？
    return True


def virtual_link_constraints(constraints, frameSet, vlinkSet, g):
    '''
    生产者虚帧先于网络链路帧先于消费者的虚帧
    参数：
        solver：求解器实例
        frameSet: 帧集合(vlid_t -> link -> [frame],两层字典)
        vlinkSet: 包含虚链路信息的集合
        g: 模型中的时间同步精度，单位：us
    '''
    # 首先取出同一条虚链路的所有帧
    for vlid_t in frameSet:
        frameSameVLink = frameSet[vlid_t]
        # 取出VLink类中的链路集合
        vl = vlinkSet[vlid_t].vl
        # 任意两条不同的相邻的Link满足:
        for i in range(len(vl)-1):
            # 取出前一个集合的最后一个帧和后一个集合的第一个帧
            linkI = vl[i]
            linkJ = vl[i+1]
            frameListLinkI = frameSameVLink[linkI]
            frameListLinkJ = frameSameVLink[linkJ]
            # 最后一个帧
            frameLastLinkI = frameListLinkI[len(frameListLinkI)-1]
            # 第一个帧
            frameFirstLinkJ = frameListLinkJ[0]
            # aCon = (linkJ.macrotick * frameFirstLinkJ.offset - linkI.delay -
            #        g >= linkI.macrotick * (frameLastLinkI.offset + frameLastLinkI.L))
            aCon = GE(
                Minus(Times(Int(linkJ.macrotick), frameFirstLinkJ.offset),
                      Int(linkI.delay + g)),
                Times(Int(linkI.macrotick), Plus(
                    frameLastLinkI.offset, Int(frameLastLinkI.L))))
            #print(aCon)
            constraints.append(aCon)
        # print(solver)
    #time_start = time.time()
    # print(solver.check())
    # print(solver.model())
    #time_end = time.time()
    # print('#计算用时：{} s'.format(time_end-time_start))
    # pdb.set_trace()

    return True


def end_to_end_latency_constraints(constraints, frameSet, vlinkSet):
    '''
    端到端延迟不能超过允许的最大延迟，即小于等于tt-message的周期。
    参数：
        solver:
        frameSet:
    '''
    # 首先选择一条虚链路
    for vlid_t in frameSet:
        frameSameVLink = frameSet[vlid_t]
        vl = vlinkSet[vlid_t].vl
        # 取Link
        firstLink = vl[0]
        lastLink = vl[len(vl)-1]
        # 取Frame
        firstFrame = frameSameVLink[firstLink][0]
        lastFrame = frameSameVLink[lastLink][len(frameSameVLink[lastLink])-1]
        # 约束
        # aCon = (lastLink.macrotick * (lastFrame.offset + lastFrame.L)
        #        <= (firstLink.macrotick * firstFrame.offset + vlinkSet[vlid_t].max_latency))
        aCon = LE(
            Times(Int(lastLink.macrotick), Plus(
                lastFrame.offset, Int(lastFrame.L))),
            Plus(Times(Int(firstLink.macrotick), firstFrame.offset),
                 Int(vlinkSet[vlid_t].max_latency)))
        #print(aCon)
        constraints.append(aCon)
    # print(solver)
    #time_start = time.time()
    # print(solver.check())
    # print(solver.model())
    #time_end = time.time()
    # print('#计算用时：{} s'.format(time_end-time_start))
    # pdb.set_trace()

    return True


def task_constraints(constraints, frameSet, vlinkSet):
    '''
    虚帧顺序执行（由其他约束规定），所有虚帧都处于调度窗口内（offset ---- deadline）
    参数：
        solver:
        frameSet:
    疑问：这里的task.offset是什么？0？还是设置值？
    '''
    # 首先选择一个条虚链路
    for vlid_t in frameSet:
        frameSameVLink = frameSet[vlid_t]
        vl = vlinkSet[vlid_t].vl
        firstSelfLink = vl[0]
        task = vlinkSet[vlid_t].task_p
        frameList = frameSameVLink[firstSelfLink]
        # 生成生成者约束
        # for frame in frameList:
        #    aCon = (frame.offset >= task.offset)
        #    print(aCon)
        #    solver.add(aCon)
        lastFrame = frameList[len(frameList)-1]
        # FIXME: 这里lastFrame.L与论文理解不同
        # aCon = (lastFrame.offset <= task.D /
        #        firstSelfLink.macrotick - lastFrame.L)
        aCon = LE(lastFrame.offset, Int(
            task.D / firstSelfLink.macrotick - lastFrame.L))
        #print(aCon)
        constraints.append(aCon)
        # 如何虚链路不是SelfLink，有消费者
        if len(vl) > 2:
            lastSelfLink = vl[len(vl)-1]
            task = vlinkSet[vlid_t].task_c
            frameList = frameSameVLink[lastSelfLink]
            # for frame in frameList:
            #    aCon = (frame.offset >= task.offset)
            #    solver.add(aCon)
            lastFrame = frameList[len(frameList)-1]
            # FIXME: 这里lastFrame.L与论文理解不同
            # aCon = (lastFrame.offset <= task.D /
            #        lastSelfLink.macrotick - lastFrame.L)
            aCon = LE(lastFrame.offset, Int(
                task.D / firstSelfLink.macrotick - lastFrame.L))
            #print(aCon)
            constraints.append(aCon)
    # print(solver)
    # print(solver.check())
    # print(solver.model())
    # pdb.set_trace()

    return True


def virtual_frame_sequence_constraints(constraints, frameSet, vlinkSet):
    '''
    链路约束规定了不同任务的虚帧不会重叠，同样同一个任务的不同虚帧也不同重叠
    注意不同的是，同一节点上不会有精度问题
    参数：
        solver:
        frameSet:
    '''
    # 首先选择一个条虚链路
    for vlid_t in frameSet:
        frameSameVLink = frameSet[vlid_t]
        vl = vlinkSet[vlid_t].vl
        firstSelfLink = vl[0]

        frameList = frameSameVLink[firstSelfLink]
        # 1.生成生成者约束
        for frameId in range(len(frameList)-1):
            frameI = frameList[frameId]
            frameJ = frameList[frameId+1]
            #aCon = (frameJ.offset >= frameI.offset + frameI.L)
            aCon = GE(frameJ.offset, Plus(frameI.offset, Int(frameI.L)))
            #print(aCon)
            constraints.append(aCon)

        # 2.如果虚链路不是SelfLink，有消费者
        if len(vl) > 2:
            lastSelfLink = vl[len(vl)-1]

            frameList = frameSameVLink[lastSelfLink]
            for frameId in range(len(frameList)-1):
                frameI = frameList[frameId]
                frameJ = frameList[frameId+1]
                #aCon = (frameJ.offset >= frameI.offset + frameI.L)
                aCon = GE(frameJ.offset, Plus(frameI.offset, Int(frameI.L)))
                #print(aCon)
                constraints.append(aCon)
    # print(solver)
    # pdb.set_trace()
    return True


def task_precedence_contraints(constraints, frameSetSortByTask, taskA, taskB):
    '''
    任务A优先于任务B：任务A必须先于任务B完成。
    '''
    frameSetA = frameSetSortByTask[taskA]
    frameSetB = frameSetSortByTask[taskB]
    lastFrameOfA = frameSetA[len(frameSetA)-1]
    fisrtFrameOfB = frameSetB[0]
    linkA = taskA.selfLink
    linkB = taskB.selfLink
    # aCon = linkB.macrotick * fisrtFrameOfB.offset >= linkA.macrotick * \
    #    (lastFrameOfA.offset + lastFrameOfA.L)
    aCon = GE(Times(Int(linkB.macrotick), fisrtFrameOfB.offset),
              Times(Int(linkA.macrotick), Plus(lastFrameOfA.offset, Int(lastFrameOfA.L))))
    #print(aCon)
    constraints.append(aCon)
    return True


def define_var(testSet):
    all_frame_set = testSet.frameSet
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for link in vl_frame_list:
            framelist = vl_frame_list[link]
            for frame in framelist:
                frame.setOffset(Symbol('offset_{}_({})_{}'.format(
                    frame.vlid, frame.lname[0]+'_'+frame.lname[1], frame.fid), INT))
                # print(frame.offset)
    return


def constraints_gen(testSet):
    if not testSet:
        return False
    # 生成Z3相关的定义
    define_var(testSet)
    # retFile = open('result/result_{}_{}.txt'.format(smtName, t), "w")
    # 约束集合
    constraints = []
    # 求解器定义
    #with Solver(name=smtName, logic=QF_LIA) as s:
    # 生成Frame约束
    frame_constraints(constraints, testSet.frameSet)
    #et = time.clock()
    #print('\t  耗时：{} s'.format(et-st))
    #
    #print('\t# 生成link constraints...')
    #st = time.clock()
    link_constraints(constraints, testSet.frameSetSortByLink)
    #et = time.clock()
    # print('\t  耗时：{} s'.format(et-st))
    # 同步精度通常为1us
    #print('\t# 生成virtual link constraints...')
    #st = time.clock()
    virtual_link_constraints(constraints, testSet.frameSet, testSet.vlinkSet, 1)
    #et = time.clock()
    #print('\t  耗时：{} s'.format(et-st))
    #
    #print('\t# 生成end to end latency constraints...')
    #st = time.clock()
    end_to_end_latency_constraints(constraints, testSet.frameSet, testSet.vlinkSet)
    #et = time.clock()
    #print('\t  耗时：{} s'.format(et-st))
    #
    #print('\t# 生成task constraints...')
    #st = time.clock()
    task_constraints(constraints, testSet.frameSet, testSet.vlinkSet)
    #et = time.clock()
    #print('\t  耗时：{} s'.format(et-st))
    #
    #print('\t# 生成virtual frame sequence constraints...')
    #st = time.clock()
    virtual_frame_sequence_constraints(
        constraints, testSet.frameSet, testSet.vlinkSet)
    # pdb.set_trace()
    
    #retFile.close()

    return constraints
