__author__ = 'aaminov'


import networkx as nx
import matplotlib.pyplot as plt


if __name__ == "__main__":

    networkFile = "smallExamples/net20_30.net"
    # G = nx.read_pajek(networkFile)
    G = nx.fast_gnp_random_graph(20, 0.2)

    print G
    nx.draw(G)
    plt.show(block=False)

    nodeList = G.nodes()

    for v in nodeList:
        print v
        depth = 0
        tree = nx.Graph()
        tree.add_node((depth, v))

        print tree


    pass

