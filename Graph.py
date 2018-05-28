from Link import Link


class Graph:
    """graph class"""
    #nodeSet = []
    #linkSet = []

    def __init__(self):
        self.isNull = True
        pass

    def initNodeSet(self, nodeSet):
        self.nodeSet = nodeSet
        self.isNull = False

    def initLinkSet(self, linkSet):
        self.linkSet = linkSet
        self.isNull = False

    def find_path(self, src):
        '''
        采用迪杰斯特拉算法简单的生成整个网络拓扑的路由
        目前不考虑负载均衡
        '''
        if not self.isNull:
            return None

        # 生成到达矩阵
        links = self.linkSet  # 图中所有的链路
        nodestrings = self.nodeSet  # 图中所有的节点
        nodes = [i for i in range(len(nodestrings))]
        gList = [[float('inf') for col in range(len(nodes))]
                for row in range(len(nodes))]
        for link in links:
            node_a = link[0]
            node_b = link[1]
            index_a = nodestrings.index(node_a)
            index_b = nodestrings.index(node_b)
            gList[index_a][index_b] = 1
        for i in range(len(nodes)):
            gList[i][i] = 0
        # print(gList)
        visited = []  # 表示已经路由到最短路径的节点集合

        if src in nodes:
            visited.append(src)
            nodes.remove(src)
        else:
            return None

        distance = {src: 0}  # 记录源节点到各个节点的距离
        for i in nodes:
            distance[i] = gList[src][i]
        # print(distance)
        path = {src: {src: []}}  # 记录源节点到每个节点的路径
        k = pre = src
        while nodes:
            mid_distance = float('inf')
            for v in visited:
                for d in nodes:
                    new_distance = gList[src][v] + gList[v][d]
                    if new_distance < mid_distance:
                        mid_distance = new_distance
                        gList[src][d] = new_distance  # 更新距离
                        k = d
                        pre = v

            distance[k] = mid_distance  # 最短路径
            path[src][k] = [i for i in path[src][pre]]
            path[src][k].append(k)
            # 更新两个节点集合
            visited.append(k)
            nodes.remove(k)
            # print(visited, nodes)  # 输出
        # return path, distance
        return path