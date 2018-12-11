from Typing.TestSet import TestSet
from Typing.Nodes import Node
import BenchGeneration as BG
import ConstraintGeneration as CG 
import SampleTupo as TUPO

from multiprocessing import Process
from pysmt.shortcuts import Solver, is_sat
from pysmt.logics import QF_LIA
import networkx as NX

import time

def run_z3(mTestSet, t, constraints):
    retFile = open('result/result_{}_{}.txt'.format('z3', t), "w")
    print('# 调用{}计算中...'.format('z3'))
    with Solver(name='z3', logic=QF_LIA) as s:
        # add constraints
        for c in constraints:
            s.add_assertion(c)
        st = time.clock()
        if s.solve():
            et = time.clock()
            print('# {}耗时：{} s'.format('z3',et-st))
            for vlid_t in mTestSet.frameSet:
                frameSameVLink = mTestSet.frameSet[vlid_t]
                for link in frameSameVLink:
                    frameSameLink = frameSameVLink[link]
                    for frame in frameSameLink:
                        retFile.writelines("%s = %s\n" %(frame.offset, s.get_value(frame.offset)))
        else:
            et = time.clock()
            print('# {}耗时：{} s'.format('z3',et-st))
            print('# {}没有可行解...'.format('z3'))

    retFile.close()

def run_yices(mTestSet, t, constraints):
    retFile = open('result/result_{}_{}.txt'.format('yices', t), "w")
    print('# 调用{}计算中...'.format('yices'))
    with Solver(name='yices', logic=QF_LIA) as s:
        # add constraints
        for c in constraints:
            s.add_assertion(c)
        st = time.clock()
        if s.solve():
            et = time.clock()
            print('# {}耗时：{} s'.format('yices',et-st))
            for vlid_t in mTestSet.frameSet:
                frameSameVLink = mTestSet.frameSet[vlid_t]
                for link in frameSameVLink:
                    frameSameLink = frameSameVLink[link]
                    for frame in frameSameLink:
                        retFile.writelines("%s = %s\n" %(frame.offset, s.get_value(frame.offset)))
        else:
            et = time.clock()
            print('# {}耗时：{} s'.format('z3',et-st))
            print('# {}没有可行解...'.format('z3'))

    retFile.close()


if __name__ == '__main__':
    # 生成拓扑图
    endSystemNum, switchNum, smallGraph = TUPO.get_small_tupo()
    freeTaskNum, comTaskNum = 8, 8 # 每个终端节点的任务个数，分为Free Task和Commun Task
    # 初始化Test Set
    mTestSet = TestSet(endSystemNum, switchNum, freeTaskNum, comTaskNum, smallGraph)
    # 周期族，测试用
    peroidSet_1 = [10000, 20000, 25000, 50000, 100000]
    peroidSet_2 = [10000, 30000, 100000]
    peroidSet_3 = [50000, 75000]
    peroidSet_4 = [50000, 60000]
    peroidSet_5 = [10000, 20000, 25000, 50000, 90000]

    print('###### 执行One_Shot算法 ######')
    #生产Result文件的时间戳
    timestamp = int(time.time())
    print('# 生成测试集', end=',')
    st = time.clock()
    # 利用率设置为0.5，任务调度粒度为250微秒
    BG.gen_testSet(mTestSet, peroidSet_3, 0.1, 250)
    et = time.clock()
    print('  耗时：{} s'.format(et-st))

    #生成约束
    print('# 生成约束集...')
    st = time.clock()
    constraints = CG.constraints_gen(mTestSet)
    et = time.clock()
    print('  耗时：{} s'.format(et-st))

    # p_z3 = Process(target=run_z3, args=(mTestSet,timestamp, constraints))
    p_yices = Process(target=run_yices, args=(mTestSet,timestamp, constraints))

    # p_z3.start()
    p_yices.start()

    p_yices.join()
    # p_z3.join()
