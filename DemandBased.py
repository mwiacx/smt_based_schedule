from Typing.TestSet import TestSet

import time
import benchmark_generation
import constraint_generation

def uCheck(testSet):
    return True

def vlCheck(testSet):
    return True

def run_z3(mtestSet, t, constraints):
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
            for vlid_t in mtestSet.frameSet:
                frameSameVLink = mtestSet.frameSet[vlid_t]
                for link in frameSameVLink:
                    frameSameLink = frameSameVLink[link]
                    for frame in frameSameLink:
                        retFile.writelines("%s = %s\n" %(frame.offset, s.get_value(frame.offset)))
        else:
            et = time.clock()
            print('# {}耗时：{} s'.format('z3',et-st))
            print('# {}没有可行解...'.format('z3'))

    retFile.close()

def run_yices(mtestSet, t, constraints):
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
            for vlid_t in mtestSet.frameSet:
                frameSameVLink = mtestSet.frameSet[vlid_t]
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
    mtestSet = TestSet(4, 2, 8, 8)
    peroidSet_1 = [10000, 20000, 25000, 50000, 100000]
    peroidSet_2 = [10000, 30000, 100000]
    peroidSet_3 = [50000, 75000]
    peroidSet_4 = [50000, 60000]
    peroidSet_5 = [10000, 20000, 25000, 50000, 90000]
    print('###### 执行demand-based算法 ######')
    print('# 生成测试集', end=',')
    st = time.clock()
    benchmark_generation.generate(mtestSet, peroidSet_3, 0.1, 250)
    et = time.clock()
    print('  耗时：{} s'.format(et-st))
    print('# 调用SMT求解器')
    # constraint_generation.z3_run(mtestSet)
    S = []
    if uCheck(mtestSet) and vlCheck(mtestSet):
        f = False
        edfFrameSet = mtestSet.freeFrameSet
        smtFrameSet = mtestSet.comFrameSet
        while not f:
            constraints = constraint_generation.constraints_gen(mtestSet) #FIXME: should be smtFrameSet!
            s = run_yices(mtestSet, timestamp, constraints) #FIXME: s?
            if s:
                taskSet_d = demand_check() #FIXME: args?
                if taskSet_d:
                    edfFrameSet, dFrameSet = edfFrameSet.selfSplit(taskSet_d)
                    smtFrameSet = smtFrameSet.addFrameSet(dFrameSet)
                else:
                    f = True
                    if edfFrameSet:
                        s += EDFSim() #FIXME: funcname? args?
            else:
                f = True

    print S
    #FIXME: visual?
