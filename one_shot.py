from TestSet import TestSet
import benchmark_generation
# import constraint_generation


if __name__ == '__main__':
    mtestSet = TestSet(4, 2)
    peroidSet_1 = [10000, 20000, 25000, 50000, 100000]
    peroidSet_2 = [10000, 30000, 100000]
    peroidSet_3 = [50000, 75000]
    benchmark_generation.generate(mtestSet, peroidSet_2, 0.5, 250)
    # constraint_generation.z3_run(mtestSet)