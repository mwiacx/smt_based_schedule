import sys
sys.path.append('/home/cx/mCode/smt_based_schedule')#add father dir to import Typing.FrameSet
#print(sys.path)
from Typing.FrameSet import FrameSet
from Typing.Link import Link
from Typing.Frame import Frame

if __name__ == '__main__':

    print('frameSet Class function test.')
    '''
    Topo:
    E1--              --E2
        --          --
          --S1--S2--
        --          --
    E3--              --E4
    Vlink:
        vlid=0, E1 -> S1 -> S2 -> E2
        vlid=1, E3 -> S1 -> S2 -> E4
        vlid=2, E1 -> S1 -> E3
    Link:
        E1->S1, S1->S2, S2->E2
        E3->S1, S2->E4
        S1->E3
    FrameList(everyone):
        [new Frame(vlid, fid...)]
    '''

    fs1 = FrameSet()

    #Create vlldict
    fs1.addFrameIndex(0, ("E1", "S1"), 0)
    fs1.addFrameIndex(0, ("S1", "S2"), 1)
    fs1.addFrameIndex(0, ("S2", "E2"), 2)

    fs1.addFrameIndex(1, ("E3", "S1"), 3)
    fs1.addFrameIndex(1, ("S1", "S2"), 4)
    fs1.addFrameIndex(1, ("S2", "E4"), 5)

    fs1.addFrameIndex(2, ("E1", "S1"), 5)
    fs1.addFrameIndex(2, ("S1", "E3"), 6)

    #Create tdict
    count = 7
    for i in range(1, 5):
        fs1.addTaskIndex('E{}'.format(i), count)
        fs1.addTaskIndex('E{}'.format(i), count+1)
        fs1.addFrameIndex(2+i, ('E{}'.format(i), 'E{}'.format(i)), count)
        fs1.addFrameIndex(2+i, ('E{}'.format(i), 'E{}'.format(i)), count+1)
        count = count + 2

    print("#TEST: fs1.vlldict={}\n".format(fs1.vlldict))
    print("#TEST: fs1.lvldict={}\n".format(fs1.lvldict))
    print("#TEST: fs1.tdict={}\n\n".format(fs1.tdict))

    fs1, theother = fs1.selfSplit(['E1', 'E2'])
    print("#TEST: theother.vlldict={}\n".format(theother.vlldict))
    print("#TEST: theother.lvldict={}\n".format(theother.lvldict))
    print("#TEST: theother.tdict={}\n".format(theother.tdict))
    print("#TEST: theother.mdict={}\n\n".format(theother.mdict))

    fs1.addFrameSet(theother)
    print("#TEST: fs1.vlldict={}\n".format(fs1.vlldict))
    print("#TEST: fs1.lvldict={}\n".format(fs1.lvldict))
    print("#TEST: fs1.tdict={}\n\n".format(fs1.tdict))
