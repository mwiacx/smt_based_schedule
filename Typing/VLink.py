class Message:
    """Message module"""

    def __init__(self, peroid, size):
        self.peroid = peroid
        self.size = size

class VLink:
    """Virtual Link module"""
    #vlid = 0 # virtual link id
    #isSelfLink = False
    #vl = [] # List of Link
    #max_latency = 0 # us

    def __init__(self, vlid, vl, max_latency):
        self.vlid = vlid
        self.vl = vl
        self.message = None
        self.max_latency = max_latency
        self.isSelfLink = False

    def setTaskPair(self, taskp, taskc):
        self.taskp = taskp
        self.taskc = taskc

    def setMessageInfo(self, peroid, size):
        self.message = Message(peroid, size)

    def setSelfLinkFlag(self):
        self.isSelfLink = True