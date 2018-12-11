from Typing.FrameSet import FrameSet
from Typing.Nodes import Task
from Typing.VLink import VLink


class TestSet:
    """ 
    类描述：
        schedule synthesis data set
    成员变量：
        nodeNum:
        switchNum:
        freeTaskNum:
        comTaskNum:
        graph:
        comFrameSet:
        freeFrameSet:
        vLinkSet:
    """

    def __init__(self, node_num, switch_num, free_task_num, comm_task_num, graph):
        self.node_num = node_num
        self.switch_num = switch_num
        self.free_task_num = free_task_num
        self.comm_task_num = comm_task_num
        #self.messageSet = []
        self.graph = graph
        #
        self.comm_frame_set = FrameSet()
        self.free_frame_set = FrameSet()
        self.vlink_set = []

    def add_vlink(self, vlink):
        self.vlink_set.append(vlink)

    #def initMessageSet(self, mSet):
    #    self.messageSet = mSet

    #def addMessage(self, mmessage):
    #    self.messageSet.append(mmessage)
