from Typing.Graph import Graph
from Typing.FrameSet import FrameSet
from Typing.Message import Message
from Typing.Task import Task
from Typing.VLink import VLink


class TestSet:
    """ schedule synthesis data set """

    def __init__(self, nodeNum, switchNum, free_task_num, com_task_num, graph):
        self.graph = graph
        self.comFrameSet = FrameSet()
        self.freeFrameSet = FrameSet()
        self.vlinkSet = []
        self.linkSet = {}
        #self.frameSet = {}
        #self.taskFrameSet = {}
        #self.frameSetSortByLink = {}
        self.messageSet = []
        self.taskSet = {}
        self.nodeNum = nodeNum
        self.switchNum = switchNum
        self.free_task_num = free_task_num
        self.com_task_num = com_task_num

    def initLinkSet(self, linkSet):
        self.linkSet = linkSet

    def addVLink(self, vlink):
        self.vlinkSet.append(vlink)

    def initMessageSet(self, mSet):
        self.messageSet = mSet

    def initTaskSet(self, taskSet):
        self.taskSet = taskSet

    def addMessage(self, mmessage):
        self.messageSet.append(mmessage)
