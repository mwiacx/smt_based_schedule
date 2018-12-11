class Frame:
    """Frame module"""
    #offest = 0 # macrotick
    #T = 0 # macrotick
    #L = 0 # macrotick

    def __init__(self, vlid, fid, lname):
        self.fid = fid # Frame id
        self.vlid = vlid # virtual link id
        self.lname = lname # link id
        self.T = 0
        self.L = 0

    def setPeroid(self, peroid):
        self.T = peroid

    def setDuration(self, duration):
        self.L = duration

    def setOffset(self, offset):
        self.offset = offset
