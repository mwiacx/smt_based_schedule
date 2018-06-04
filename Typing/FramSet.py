from Typing.Frame import Frame

class FrameSet:
    '''
    FrameSet：multi-index Frame Set
    '''

    def __init__(self):
        self.vlldict = {} # Indexed by (vlid, link) or (link, vlid), 有序 
        self.lvldict = {}
        self.tdict = {}
        self.mdict = {}
    '''
    添加索引：(vlid, link) tuple ---> frame list
    表示： 同一vlink下的每一个link包含的frame
    '''
    def addVlinkLinkIndex(self, vlid, link, frame):
        # check key
        if not vlid in self.vlldict:
            self.vlldict[vlid] = {}
        framedict = self.vlldict[vlid]
        if not link in framedict:
            framedict[link] = []
        # add frame to list
        framedict[link].append(frame)

    '''
    添加索引：(link, vlid) tuple ---> frame list
    表示： 通过同一link的不同vlink包含的frame
    '''
    def addLinkVlinkIndex(self, vlid, link, frame):
        # check key
        if not link in self.lvldict:
            self.lvldict[link] = {}
        framedict = self.lvldict[link]
        if not vlid in framedict:
            framedict[vlid] = []
        # add frame to list
        framedict[vlid].append(frame)

    '''
    添加索引：task ---> frame list
    表示： 同一task包含的所有frame
    '''
    def addTaskIndex(self, task, frame):
        # check key
        if not task in self.tdict:
            self.tdict[task] = []
        # add it to list
        self.tdict[task].append(frame)

    '''
    添加索引：message ---> frame list
    表示：一个消息对应的所有frame
    '''
    def addMessageIndex(self, message, frame):
        # check key
        if not message in self.mdict:
            self.mdict[message] = []
        # add.
        self.mdict[message].append(frame)

    '''
    按照要求将FrameSet分解为两个子FrameSet
    '''
    def selfSplit(self, subtasklist, mflist):
        theother = FrameSet()
        # Spilt tdict
        for task in subtasklist:
            if task in self.tdict:
                flist = self.tdict.pop(task)
                theother.tdict[task] = flist
            else:
                print('###Waring: 将不在FrameSet中的Task从tdict中分离 in function selfSpit.')
        # Spilt vlldict
        # 首先构造一个subtasklit对应的frame的集合(Set)
        flist = []
        flist += mflist
        for task in subtasklist:
            flist += self.tdict[task]
        fset = set(flist)
        # 将fset中的frame从vlldict分离出来
        for key in self.vlldict:
            newlist = []
            oldlist = self.vlldict[key]
            for f in fset:
                if f in oldlist:
                    oldlist.remove(f)
                    newlist.append(f)
                else:
                    pass
            #
            theother.vlldict[key] = newlist
        # return
        return self, theother