from Typing.Nodes import Node
from Typing.Nodes import NodeType
import networkx as nx

def get_small_tupo(es_sc, ss_sc, ldelay, sldelay, lmt, slmt):
    '''
    tupo:
    e1--        --e3
        --s1--s2
    e2--        --e4

    nodes:
        endsystem num: 4
        switch num: 2
        total: 6
    params:
        es_sc: speed_coefficient between endsystem and switch
        ss_sc: speed_coefficient between two switches
        ldelay: link delay
        lmt: link macrotick
        sldelay: selflink delay
        slmt: selflink macrotick
    '''
    g = nx.Graph()
    node_dict = {}
    # add nodes
    for i in range(4):
        node_dict[i] = Node(nid=i, ntype=NodeType.ENDSYSTEM)
        g.add_node(node_dict[i])
    for i in range(4,6):
        node_dict[i] = Node(nid=i, ntype=NodeType.SWITCH)
        g.add_node(node_dict[i])
    # add links
    for i in range(0,2):
        g.add_edge(node_dict[i], node_dict[4], sc=es_sc, delay=ldelay, mt=lmt)
    for i in range(2,4):
        g.add_edge(node_dict[i], node_dict[5], sc=es_sc, delay=ldelay, mt=lmt)
    g.add_edge(node_dict[4], node_dict[5], sc=ss_sc, delay=ldelay, mt=lmt)
    # add selflinks
    for i in range(4):
        #FIXME: sc = ?, now not used
        g.add_edge(node_dict[i], node_dict[i], sc=1, delay=sldelay, mt=slmt)

    return 4, 2, g

def get_mid_tupo(es_sc, ss_sc, ldelay, sldelay, lmt, slmt):
    '''
    tupo:
    e1--        --e3
        --s1--s2
    e2--        --e4

    nodes:
        endsystem num: 4
        switch num: 2
        total: 6
    params:
        es_sc: speed_coefficient between endsystem and switch
        ss_sc: speed_coefficient between two switches
        ldelay: link delay
        lmt: link macrotick
        sldelay: selflink delay
        slmt: selflink macrotick
    '''
    return 0, 0, None

def get_large_tupo(es_sc, ss_sc, ldelay, sldelay, lmt, slmt):
    '''
    tupo:
    e1--        --e3
        --s1--s2
    e2--        --e4

    nodes:
        endsystem num: 4
        switch num: 2
        total: 6
    params:
        es_sc: speed_coefficient between endsystem and switch
        ss_sc: speed_coefficient between two switches
        ldelay: link delay
        lmt: link macrotick
        sldelay: selflink delay
        slmt: selflink macrotick
    '''
    return 0, 0, None

# TEST SampleTupo:
if __name__ == '__main__':
    node_num, switch_num, graph = get_small_tupo(0.08, 0.008, 10, 250, 1, 250)
    print('endsystem and switch num:')
    print(node_num, switch_num)
    print('node info:')
    for node in graph.nodes:
        print('node.nid = {}, node.ntype = {}, node.task_lists = {}'.format(node.nid, node.ntype, node.task_lists))
    print('link info:')
    for edge, datadict in graph.edges.items():
        if edge[0].nid == edge[1].nid:
            continue
        print('edge=({},{}), datadict={}'.format(edge[0].nid, edge[1].nid, datadict))
    print('selflink info:')
    for node1, node2, datadict in nx.selfloop_edges(graph, data=True):
        print('edge=({},{}), datadict={}'.format(node1.nid, node2.nid, datadict))