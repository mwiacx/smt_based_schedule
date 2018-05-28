from Typing.Graph import Graph
from Typing.Message import Message
from Typing.Task import Task
from Typing.VLink import VLink


class TestSet:
    """ schedule synthesis data set """

    def __init__(self, nodeNum, switchNum):
        self.graph = Graph()
        self.vlinkSet = []
        self.linkSet = {}
        self.frameSet = {}
        self.taskFrameSet = {}
        self.frameSetSortByLink = {}
        self.messageSet = []
        self.taskSet = {}
        self.nodeNum = nodeNum
        self.switchNum = switchNum

    def initGraph(self, linkSet, nodeSet):
        self.graph.initNodeSet(nodeSet)
        self.graph.initLinkSet(linkSet)

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