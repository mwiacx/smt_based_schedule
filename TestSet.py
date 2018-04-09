from Graph import Graph
# form Link import Link
from Message import Message
from Task import Task
from VLink import VLink


class TestSet:
    """ schedule synthesis data set """

    def __init__(self, nodeNum, switchNum):
        self.graph = Graph()
        self.vlinkSet = []
        self.frameSet = {}
        self.messageSet = []
        self.taskSet = {}
        self.nodeNum = nodeNum
        self.switchNum = switchNum

    def initGraph(self, linkSet, nodeSet):
        self.graph.initNodeSet(nodeSet)
        self.graph.initLinkSet(linkSet)

    def addVLink(self, vlink):
        self.vlinkSet.append(vlink)

    def initMessageSet(self, mSet):
        self.messageSet = mSet

    def initTaskSet(self, taskSet):
        self.taskSet = taskSet

    def addMessage(self, mmessage):
        self.messageSet.append(mmessage)
