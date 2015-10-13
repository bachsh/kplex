__author__ = 'aaminov'


import networkx as nx
import matplotlib.pyplot as plt
from copy import copy
from time import sleep

ROOT = (-1, -1, None)
global_index = 0

def olderBrother(T, v, vb):
    p = T.predecessors(v)[0]
    return vb in T.successors(p)

def kConnectedToBranch(G, T, parent, v_cand, k):
    if parent == ROOT:
        return True
    neighbors = [x[1] for x in G.edges(v_cand)]
    # print parent, v_cand, neighbors
    count = 0 if parent[1] in neighbors else 1
    while T.predecessors(parent) != [ROOT]:
        parent = T.predecessors(parent)[0]
        # print parent, v_cand, neighbors
        count += not parent[1] in neighbors
    # print count
    return count < k


def kplexTree(G, T, parent, candidates, degree, k, ind):
    if candidates == {}:
        return ind
    candidates_orig = copy(candidates)
    # print "parent {}. Candidates: {}. degree: {}".format(parent, candidates, degree)
    for v_cand in candidates_orig:
        if kConnectedToBranch(G, T, parent, v_cand, k):
            ind += 1
            newLeaf = (degree+1, v_cand, ind)
            T.add_node(newLeaf)
            T.add_edge(parent, newLeaf)
    succList = T.successors(parent)
    # print "created leaves: {}".format(succList)
    newCandidates = {x[1] for x in succList}
    for node in succList:
        newCandidates -= {node[1]}
        # print "new siblings = {} sent to node {}".format(newCandidates, node)
        ind = kplexTree(G, T, node, newCandidates, degree+1, k, ind)
    return ind


def kplexFromLeaf(T, leaf):
    if leaf == ROOT:
        return set()
    print leaf
    res = kplexFromLeaf(T, T.predecessors(leaf)[0])
    res.add(leaf[1])
    return res


def kplexesFromTree(T, node):
    succ = T.successors(node)
    if succ == []:
        kplex = kplexFromLeaf(T, node)
        return [kplex]
    kplexes = []
    for v in succ:
        kplexes.extend(kplexesFromTree(T, v))
    return kplexes



if __name__ == "__main__":

    networkFile = "smallExamples/net20_30.net"
    # G = nx.read_pajek(networkFile)
    G = nx.fast_gnp_random_graph(20, 0.2)

    G = nx.Graph({
        0: {1,2},
        1: {0, 4,5},
        2: {3,4,0},
        3: {2,4,5},
        4: {1,2,3},
        5: {1,2,3}
    })


    pos=nx.spring_layout(G) # positions for all nodes

    # nodes
    nx.draw_networkx_nodes(G,pos,node_size=700)

    # edges
    nx.draw_networkx_edges(G,pos, width=3)

    # labels
    nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

    plt.axis('off')
    plt.show(block=False)

    N = len(G.nodes())
    print "Nodes: {}".format(G.nodes())

    tree = nx.DiGraph()
    tree.add_node(ROOT)
    candidates = set(range(N))

    kplexTree(G, tree, ROOT, candidates, -1, 1, 0)
    print tree.nodes()
    sleep(0.1)

    print kplexesFromTree(tree, ROOT)

    plt.figure()

    raw_input("Press <Enter> to cont")
