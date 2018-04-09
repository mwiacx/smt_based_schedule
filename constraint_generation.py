import math
from z3 import *


def frame_constraints(slover, testSet):
    all_frame_set = testSet.frameSet
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for frame in vl_frame_list:
            slover.add(frame.offest > 0, frame.offest < frame.T - frame.L)
    return True


def link_constraints():

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
            frame = vl_frame_list[link]
            frame.offest = Int('frame_{}_{}_{}.offest'.format(
                frame.vlid, frame.lname, frame.fid))
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

    return True
