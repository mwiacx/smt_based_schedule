class Task(object):
    def __init__(self, **kv):
        self.C = 0
        self.D = 0
        self.T = 0
        self.offset = 0

        # vlink id
        self.vlid = 0
        # task id（高16为表示节点编号，低16位表示节点内任务编号）
        self.tid = 0

        '''
        a task may has more than one sid, indexed from 1 to n
        if a task has no supper tasks, the sid shall be set to 0
        '''
        self.sid = 0

        for k, v in kv.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise Exception(
                    "No property has name %s in the class Task" % k)
