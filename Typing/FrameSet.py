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
    表示：同一task包含的所有frame
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
    For Demand-based SMT schedule synthesis
    这个函数只应该用于拆分Gamma_edf, 不应该包含消息Frame
    '''
    def selfSplit(self, subtasklist):
        theother = FrameSet()
        # Spilt tdict
        for task in subtasklist:
            if task in self.tdict:
                flist = self.tdict.pop(task)
                theother.tdict[task] = flist
            else:
                print('###Waring: 将不在FrameSet中的Task从tdict中分离in function selfSpit.')
                return self, None
        # Spilt vlldict
        # 首先构造一个subtasklit对应的frame的集合(list)
        subflist = []
        for task in subtasklist:
            subflist += self.tdict[task]

        # 将subflist中的frame从vlldict分离出来
        for vlid in self.vlldict:
            ldict = self.vlldict[vlid]
            theother.vlldict[vlid] = {}
            for link in ldict:
                newlist = []
                oldlist = ldict[link]
                for f in subflist:
                    if f in oldlist:
                        oldlist.remove(f)
                        newlist.append(f)
                # 添加到theother
                theother.vlldict[vlid][link] = newlist
                # 如果oldlist空了，删除相关索引
                if not oldlist:
                    vldict.pop(link)
            # 如果vldict空了，删除相关索引
            if not ldict:
                self.lvldict.pop(vlid)

        # 将flist中的frame从lvldict分离出来
        for link in self.lvldict:
            vldict = self.lvldict[link]
            theother.lvldict[link] = {}
            for vlid in vldict:
                newlist = []
                oldlist = vldict[vlid]
                for f in subflist:
                    if f in oldlist:
                        oldlist.remove(f)
                        newlist.append(f)
                # 添加到theother
                theother.lvldict[vlid][link] = newlist
                # 如果oldlist空了，删除相关索引
                if not oldlist:
                    vldict.pop(vlid)
            # 如果vldict空了，删除相关索引
            if not vldict:
                self.lvldict.pop(link)

        # return
        return self, theother

    '''
    将一个FrameSet(应只包含selflink对应的Frame)融合进自身
    '''
    def addFrameSet(self, otherFrameSet):
        #check if they are selflink frames
        if not otherFrameSet.mdict.
        #mix tdict
        odict = otherFrameSet.tdict
        sdict = self.tdict
        for key in odict:
            sdict[key] = odict[key]

        #mix vlldict
        odict = otherFrameSet.vlldict
        sdict = self.vlldict
        for vlid in odict:
            oldict = odict[vlid]
            if not vlid in sdict:
                sdict[vlid] = {}
            for link in oldict:
                flist = oldict[link]
                if not link in sdict[vlid]:
                    sdict[vlid][link] = flist
                else:
                    sdict[vlid][link] += flist

        #mix lvldict
        odict = otherFrameSet.vlldict
        sdict = self.vlldict
        for link in odict:
            ovldict = odict[link]
            if not link in sdict:
                sdict[link] = {}
            for vlid in ovldict:
                flist = ovldict[vlid]
                if not vlid in sdict[link]:
                    sdict[link][vlid] = flist
                else:
                    sdict[link][vlid] += flist

        return self
