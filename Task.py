class Task:
    """Task module"""
    offest = 0 # us
    C = 100 # us
    D = 100 #us
    T = 100 #us

    def __init__(self, nid, tid):
        self.tid = tid #task id
        self.nid = nid #node id
        pass
