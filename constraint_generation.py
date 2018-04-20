import math
import pdb
import time
from z3 import *


def frame_constraints(slover, frameSet):
    '''
    向求解器中添加帧约束
        slover: z3求解器实例
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
                aCon = (frame.offset > 0, frame.offset < frame.T - frame.L)
                # print(aCon)
                slover.add(aCon)

    # print(slover)
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


def link_constraints(slover, frameSetSortedByLink):
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
                        single_link_constraint = Or(
                            (frame_i.offset + alpha * frame_i.T >=
                             frame_j.offset + beta * frame_j.T + frame_j.L),
                            (frame_j.offset + beta * frame_j.T >= frame_i.offset + alpha * frame_i.T + frame_i.L))
                        # print('alpha={},beta={}:\nconstraint={}'.format(
                        #    alpha, beta, single_link_constraint))
                        slover.add(single_link_constraint)
                # print(slover)
    # print(slover.check())
    # print(slover.model())
    # pdb.set_trace()
    # FIXME:提高效率？
    return True


def virtual_link_constraints(slover, frameSet, vlinkSet, g):
    '''
    生产者虚帧先于网络链路帧先于消费者的虚帧
    参数：
        slover：求解器实例
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
            aCon = (linkJ.macrotick * frameFirstLinkJ.offset - linkI.delay -
                    g >= linkI.macrotick * (frameLastLinkI.offset + frameLastLinkI.L))
            # print(aCon)
            slover.add(aCon)
        # print(slover)
    #time_start = time.time()
    # print(slover.check())
    # print(slover.model())
    #time_end = time.time()
    # print('#计算用时：{} s'.format(time_end-time_start))
    # pdb.set_trace()

    return True


def end_to_end_latency_constraints(slover, frameSet, vlinkSet):
    '''
    端到端延迟不能超过允许的最大延迟，即小于等于tt-message的周期。
    参数：
        slover:
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
        aCon = (lastLink.macrotick * (lastFrame.offset + lastFrame.L)
                <= (firstLink.macrotick * firstFrame.offset + vlinkSet[vlid_t].max_latency))
        # print(aCon)
        slover.add(aCon)
    # print(slover)
    #time_start = time.time()
    # print(slover.check())
    # print(slover.model())
    #time_end = time.time()
    # print('#计算用时：{} s'.format(time_end-time_start))
    # pdb.set_trace()

    return True


def task_constraints(slover, frameSet, vlinkSet):
    '''
    虚帧顺序执行（由其他约束规定），所有虚帧都处于调度窗口内（offset ---- deadline）
    参数：
        slover:
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
        #    slover.add(aCon)
        lastFrame = frameList[len(frameList)-1]
        # FIXME: 这里lastFrame.L与论文理解不同
        aCon = (lastFrame.offset <= task.D /
                firstSelfLink.macrotick - lastFrame.L)
        slover.add(aCon)
        # 如何虚链路不是SelfLink，有消费者
        if len(vl) > 2:
            lastSelfLink = vl[len(vl)-1]
            task = vlinkSet[vlid_t].task_c
            frameList = frameSameVLink[lastSelfLink]
            # for frame in frameList:
            #    aCon = (frame.offset >= task.offset)
            #    slover.add(aCon)
            lastFrame = frameList[len(frameList)-1]
            # FIXME: 这里lastFrame.L与论文理解不同
            aCon = (lastFrame.offset <= task.D /
                    lastSelfLink.macrotick - lastFrame.L)
            slover.add(aCon)
    # print(slover)
    # print(slover.check())
    # print(slover.model())
    # pdb.set_trace()

    return True


def virtual_frame_sequence_constraints(slover, frameSet, vlinkSet):
    '''
    链路约束规定了不同任务的虚帧不会重叠，同样同一个任务的不同虚帧也不同重叠
    注意不同的是，同一节点上不会有精度问题
    参数：
        slover:
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
            aCon = (frameJ.offset >= frameI.offset + frameI.L)
            # print(aCon)
            slover.add(aCon)

        # 2.如果虚链路不是SelfLink，有消费者
        if len(vl) > 2:
            lastSelfLink = vl[len(vl)-1]

            frameList = frameSameVLink[lastSelfLink]
            for frameId in range(len(frameList)-1):
                frameI = frameList[frameId]
                frameJ = frameList[frameId+1]
                aCon = (frameJ.offset >= frameI.offset + frameI.L)
                # print(aCon)
                slover.add(aCon)
    # print(slover)
    # pdb.set_trace()
    return True


def task_precedence_contraints(slover, frameSetSortByTask, taskA, taskB):
    '''
    任务A优先于任务B：任务A必须先于任务B完成。
    '''
    frameSetA = frameSetSortByTask[taskA]
    frameSetB = frameSetSortByTask[taskB]
    lastFrameOfA = frameSetA[len(frameSetA)-1]
    fisrtFrameOfB = frameSetB[0]
    linkA = taskA.selfLink
    linkB = taskB.selfLink
    aCon = linkB.macrotick * fisrtFrameOfB.offset >= linkA.macrotick * \
        (lastFrameOfA.offset + lastFrameOfA.L)
    print(aCon)
    slover.add(aCon)
    return True


def define_var(testSet):
    all_frame_set = testSet.frameSet
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for link in vl_frame_list:
            framelist = vl_frame_list[link]
            for frame in framelist:
                frame.offset = Int('offset_{}_({})_{}'.format(
                    frame.vlid, frame.lname[0]+'_'+frame.lname[1], frame.fid))
                # print(frame.offset)
    return


def z3_run(testSet):
    if not testSet:
        return False
    # 生成Z3相关的定义
    define_var(testSet)
    # 求解器定义
    s = Solver()
    # 生成Frame约束
    print('\t# 生成frame constraints...')
    st = time.clock()
    frame_constraints(s, testSet.frameSet)
    et = time.clock()
    print('\t  耗时：{} s'.format(et-st))
    #
    print('\t# 生成link constraints...')
    st = time.clock()
    link_constraints(s, testSet.frameSetSortByLink)
    et = time.clock()
    print('\t  耗时：{} s'.format(et-st))
    # 同步精度通常为1us
    print('\t# 生成virtual link constraints...')
    st = time.clock()
    virtual_link_constraints(s, testSet.frameSet, testSet.vlinkSet, 1)
    et = time.clock()
    print('\t  耗时：{} s'.format(et-st))
    #
    print('\t# 生成end to end latency constraints...')
    st = time.clock()
    end_to_end_latency_constraints(s, testSet.frameSet, testSet.vlinkSet)
    et = time.clock()
    print('\t  耗时：{} s'.format(et-st))
    #
    print('\t# 生成task constraints...')
    st = time.clock()
    task_constraints(s, testSet.frameSet, testSet.vlinkSet)
    et = time.clock()
    print('\t  耗时：{} s'.format(et-st))
    #
    print('\t# 生成virtual frame sequence constraints...')
    st = time.clock()
    virtual_frame_sequence_constraints(s, testSet.frameSet, testSet.vlinkSet)
    et = time.clock()
    print('\t  耗时：{} s'.format(et-st))
    #
    print('# Z3计算中...')
    st = time.clock()
    if s.check() == sat:
        et = time.clock()
        print('  耗时：{} s'.format(et-st))
        print('# 已求解，一个可行解为：')
        # resultFile = open('result/result_{}.txt'.format(int(time.time())), "w")
        model = s.model()
        print(model)
        # resultFile.write(model)

    else:
        et = time.clock()
        print('  耗时：{} s'.format(et-st))
        print('# 没有可行解...')
    # pdb.set_trace()

    return True
