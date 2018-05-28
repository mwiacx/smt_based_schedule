from Typing.Link import Link

class VLink:
    """Virtual Link module"""
    #vlid = 0 # virtual link id
    #isSelfLink = False
    #vl = [] # List of Link
    #max_latency = 0 # us

    def __init__(self, vlid, vl, max_latency):
        self.vlid = vlid
        self.vl = vl
        self.max_latency = max_latency
        self.isSelfLink = False

    def setTaskPair(self, task_p, task_c):
        self.task_p = task_p
        self.task_c = task_c

    def setSelfLinkFlag(self):
        self.isSelfLink = True