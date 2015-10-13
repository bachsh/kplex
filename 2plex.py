__author__ = 'aaminov'


import networkx as nx
import matplotlib.pyplot as plt


def olderBrother(T, v, vb):
    p = T.predecessors(v)[0]
    return vb in T.successors(p)

def kConnectedToBranch(G, T, parent, v_cand, k):
    neighbors = G.edges(v_cand)
    count = 0 if parent[1] in neighbors else 1
    while count < k and T.predecessors(parent) != []:
        parent = T.predecessors(parent)[0]
        count += not parent[1] in neighbors
    return count < k

def kplexTree(G, T, parent, candidates, degree, k):
    if candidates == {}:
        return
    for v_cand in candidates:
        if kConnectedToBranch(G, T, parent, v_cand, k):
            T.add_node((degree+1, v_cand))
            T.add_edge((degree, parent), (degree+1, v_cand))
        kplexTree(G, T, parent, candidates-{v_cand}, degree+1)


if __name__ == "__main__":

    networkFile = "smallExamples/net20_30.net"
    # G = nx.read_pajek(networkFile)
    G = nx.fast_gnp_random_graph(20, 0.2)

    print G
    nx.draw(G)
    plt.show(block=False)

    nodeList = G.nodes()
    N = len(G.nodes())

    trees = list()

    candidates = range(N)

    for v in nodeList:
        tree = nx.DiGraph()
        tree.add_node((0, v))




        trees.append(tree)


    pass

