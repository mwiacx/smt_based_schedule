'''
class Task:
    """Task module"""
    #offset = 0  # us
    #C = 100  # us
    #D = 100  # us
    #T = 100  # us
    #vlid = 0

    def __init__(self, nid, tid):
        self.tid = tid  # task id
        self.nid = nid  # node id
        self.C = -1 #us
        self.T = -1 #us
        self.D = -1 #us

    def setVlid(self, vlid):
        self.vlid = vlid

    def setSelfLink(self, selfLink):
        self.selfLink = selfLink
'''
class Task(object):
    def __init__(self,**kv):
        self.C = 0
        self.D = 0
        self.T = 0
        self.offset = 0

        # vlink id
        self.vlid = 0
        # task id
        self.tid = 0

        ''' 
        a task may has more than one sid, indexed from 1 to n
        if a task has no supper tasks, the sid shall be set to 0
        '''
        self.sid  = 0

        for k,v in kv.items():
            if hasattr(self,k):
                setattr(self,k,v)
            else:
                raise Exception("No property has name %s in class Task" % k )