from enum import Enum
from Typing.Task import Task

class NodeType(Enum):
    ENDSYSTEM = 1
    SWITCH = 2

class Node(object):

    def __init__(self, **kv):
        self.nid = 0
        self.ntype = NodeType.ENDSYSTEM
        self.free_task_list = []
        self.comm_task_list = []

        for k, v in kv.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise Exception('No property has name %s in the class Node'%k)

