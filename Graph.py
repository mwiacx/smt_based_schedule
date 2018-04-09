from Link import Link


class Graph:
    """graph class"""
    nodeSet = []
    linkSet = []

    def __init__(self):
        pass

    def say_hi(self):
        print("Hi, module Graph")

    def addNode(self, newNode):
        self.nodeSet.append(newNode)

    def delNode(self, theNode):
        self.nodeSet.remove(theNode)

    def initNodeSet(self, nodeSet):
        self.nodeSet = nodeSet

    def addLink(self, newLink):
        self.linkSet.append(newLink)

    def delLink(self, theLink):
        self.linkSet.remove(theLink)

    def initLinkSet(self, linkSet):
        self.linkSet = linkSet
