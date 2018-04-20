from TestSet import TestSet
import time
import benchmark_generation
import constraint_generation


if __name__ == '__main__':
    mtestSet = TestSet(4, 2)
    peroidSet_1 = [10000, 20000, 25000, 50000, 100000]
    peroidSet_2 = [10000, 30000, 100000]
    peroidSet_3 = [50000, 75000]
    peroidSet_4 = [50000, 60000]
    peroidSet_5 = [10000, 20000, 25000, 50000, 90000]
    print('###### 执行One_Shot算法 ######')
    print('# 生成测试集', end=',')
    st = time.clock()
    benchmark_generation.generate(mtestSet, peroidSet_3, 0.3, 250)
    et = time.clock()
    print('  耗时：{} s'.format(et-st))
    print('# 调用Z3求解器')
    constraint_generation.z3_run(mtestSet)
