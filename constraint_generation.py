import math
from z3 import *


def frame_constraints(self):
    pass


def link_constraints(self):
    pass


def virtual_link_constraints(self):
    pass


def end_to_end_latency_constraints(self):
    pass


def task_constraints(self):
    pass


def virtual_frame_sequence_constraints(self):
    pass


def task_precedence_contraints(self):
    pass


def define_var(self, testSet):
    all_frame_set = testSet.frameSet
    for vlid_t in all_frame_set:
        vl_frame_list = all_frame_set[vlid_t]
        for frame in vl_frame_list:
            frame.offest = Real('frame_{}_{}_{}.offest'.format(
                frame.vlid, frame.lname, frame.fid))
    return


x = Real('x')
y = Real('y')
s = Solver()
s.add(x + y > 5, x > 1, y > 1)
print(s.check())
print(s.model())
