class Frame:
    """Frame module"""
    offest = 0 # macrotick
    T = 0 # macrotick
    L = 0 # macrotick

    def __init__(self, vlid, fid, lname):
        self.fid = fid # Frame id
        self.vlid = vlid # virtual link id
        self.lname = lname # link id
    
    def setPeroid(self, peroid):
        self.T = peroid

    def setDuration(self, duration):
        self.L = duration