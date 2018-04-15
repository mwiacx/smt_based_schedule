import math
from z3 import *


def frame_constraints(slover, testSet):
    all_frame_set = testSet.frameSet
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for link in vl_frame_list:
            framelist = vl_frame_list[link]
            for frame in framelist:
                slover.add(frame.offset > 0, frame.offset < frame.T - frame.L)
    return True


def link_constraints(slover, frameSetSortedByLink):
    for link in frameSetSortedByLink:
        subFrameDict = frameSetSortedByLink[link]
        frameSameLink = []
        for vlid in subFrameDict:
            frameList = subFrameDict[vlid]
            for frame in frameList:
                frameSameLink.append(frame)
        # 对于同一个物理链路的任意两个帧成立：
        
         
    return True


def virtual_link_constraints():
    pass


def end_to_end_latency_constraints():
    pass


def task_constraints():
    pass


def virtual_frame_sequence_constraints():
    pass


def task_precedence_contraints():
    pass


def define_var(testSet):
    all_frame_set = testSet.frameSet
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for link in vl_frame_list:
            framelist = vl_frame_list[link]
            for frame in framelist:
                frame.offset = Int('frame_{}_{}_{}.offset'.format(
                    frame.vlid, frame.lname, frame.fid))
                print(frame.offset)
    return


def z3_run(testSet):
    if not testSet:
        return False
    # 生成Z3相关的定义
    define_var(testSet)
    # 求解器定义
    s = Solver()
    # 生成Frame约束
    frame_constraints(s, testSet)
    print(s)

    return True
