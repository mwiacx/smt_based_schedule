class Task:
    """Task module"""
    offset = 0  # us
    C = 100  # us
    D = 100  # us
    T = 100  # us
    vlid = 0

    def __init__(self, nid, tid):
        self.tid = tid  # task id
        self.nid = nid  # node id

    def setVlid(self, vlid):
        self.vlid = vlid

    def setSelfLink(self, selfLink):
        self.selfLink = selfLink
