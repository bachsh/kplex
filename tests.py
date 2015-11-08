import networkx as nx
from kplex import kplexAlg
import kplex
import matplotlib.pyplot as plt
from time import time
import pandas as pd
import pickle
from os.path import isfile
from kplex_draw import draw_kplex
import numpy as np
from ast import literal_eval



def simpleExample():
    print "running simple example"
    N = 10
    G = nx.fast_gnp_random_graph(N, 10./N)
    N = len(G.nodes())
    k = 1

    analyzeNetwork(G, k)
    # kplexes = kplexAlg(G, k)


def timings():
    N_range = [30, 50, 100, 200, 500, 1000, 2000, 10000]
    # N_range = [5, 10, 30, 50, 100, 200]
    df = pd.DataFrame({}, columns=["|G|", "time", "num kplexes", "num max kplexes"])
    for N in N_range:
        print N
        G = nx.fast_gnp_random_graph(N, 10./N)
        start_time = time()
        kplexFull, kplexMax = kplexAlg(G, 2, verbose=True)
        run_time = time()-start_time
        print run_time
        df.loc[len(df)] = [N, run_time, len(kplexFull), len(kplexMax)]

    df.to_csv("timings.csv")
    df = df.set_index("|G|")
    print df


def readKplexes(file):
    with open(file) as f:
        content = f.readlines()
    res = []
    for line in content:
        line = line.rstrip('}\r\n').lstrip("{")
        line = line.split(",")
        print map(int, line)
        res.append(set(map(int, line)))
    return res
    # return set(map(literal_eval, content))


def analyzeNetwork(G, k=2, filename=None):
    # # Get full kplexes
    # if filename and isfile(filename+"_full"):
    #     kplexFull = pickle.load(open(filename+"_full"))
    #     print "done reading cache {}".format(len(kplexFull))
    # else:
    #     tree = nx.DiGraph()
    #     tree.add_node(kplex.ROOT)
    #     candidates = G.nodes()
    #     print "Building auxiliary tree..."
    #     kplex.kplexTree(G, tree, candidates, k)
    #     print "Done Building auxiliary tree"
    #     print "Reading all kplexes..."
    #     kplexFull = kplex.kplexesFromTree(tree)
    #     print "done reading all kplexes"
    #     if filename:
    #         print "saving cache"
    #         pickle.dump(kplexFull, open(filename+"_full", 'wb'))

    # Get max kplexes
    orig_filename = filename
    filename = "{}_k{}".format(filename, k)
    if orig_filename and isfile(filename):
        print "reading max kplexes from file {}".format(filename)
        kplexesMax = pickle.load(open(filename))
    else:
        print "finding max kplexes in the graph"
        # kplexesMax = kplex.getMaximalSets(kplexFull)
        kplexFull, kplexesMax = kplexAlg(G, k, verbose=True)
        if filename:
            print "writing max kplexes to file"
            pickle.dump(kplexesMax, open(filename, 'wb'))

    # dump maxes to file
    with open(filename+".txt", "wb") as f:
        for kplex in kplexesMax:
            f.write(",".join(kplex))
            f.write("\r\n")

    # get MCC size...
    print "Calculating MCC data"
    maxSize = max(map(len, kplexesMax))
    Lrange = range(maxSize+1, 1, -1)
    f1 = [] # |V_L|
    f2 = [] # |MCC(V_L)|
    nodes = set()
    for L in Lrange:
        kplexL = filter(lambda x: len(x) == L, kplexesMax)
        G_L = nx.Graph()
        for x in kplexL:
            Gx = G.subgraph(x)
            G_L = nx.compose(G_L, Gx)
        # for x in kplexL:
        #     nodes |= x
        # G_L = G.subgraph(nodes)
        f1.append(len(G_L.nodes()))
        MCCs = nx.connected_component_subgraphs(G_L)
        lenMCC = map(len, MCCs)
        maxLen = 0 if lenMCC==[] else max(lenMCC)
        f2.append(maxLen)

    plt.figure()
    plt.plot(Lrange, f1, label="|V_L|")
    plt.plot(Lrange, f2, label="|MCC(G_L)|")
    plt.xlabel("L")
    plt.legend()
    plt.savefig("{}_MCC_k{}.png".format(orig_filename, k))

    # get histogram for size of kplex
    print "Calculating kplex size histogram"
    kplexSizes = map(len, kplexesMax)
    # plt.hist(kplexSizes)
    plt.figure()
    plt.hist(kplexSizes, np.arange(maxSize+1)+0.5)
    plt.xlabel("L")
    plt.savefig("{}_hist_k{}.png".format(orig_filename, k))
    plt.show()


def c_elegans():
    print "Reading worm..."
    # Gd = nx.read_gml("Networks/CelegansNeural/celegansneural_trunc.gml")
    # G = Gd.to_undirected() # network is read as directed graph :)
    # G = nx.read_adjlist("Networks/CelegansNeural/celegansneural.txt")
    G = nx.read_adjlist("Networks/CelegansNeural/CEnn.txt")
    print "Done Reading worm. Worm has {} nodes and {} edges".format(len(G.nodes()), len(G.edges()))
    # compareToMathematica(G, 2, "Networks/CelegansNeural/Kplexes_CEnn.txt")
    analyzeNetwork(G, 3, "worm2")


def astroph():
    print "Reading AstroPh..."
    G = nx.read_adjlist("Networks/AstroPh/astro-ph.txt")
    G = G.to_undirected()
    print "Done Reading astro. astro has {} nodes and {} edges".format(len(G.nodes()), len(G.edges()))
    analyzeNetwork(G, 2, "astro")


def compareToMathematica(G, k, mathematicaOutputfile):
    mathRes = kplex.getMaximalSets(readKplexes(mathematicaOutputfile))
    _, kplexAlgRes = kplex.kplexAlg(G, k, verbose=True, method="wu")
    print "alg res: ", kplexAlgRes
    print "Mathematica output: ", mathRes
    print "Results OK" if kplexAlgRes == mathRes else "Results incompatible"
    plt.hist(map(len, kplexAlgRes))
    plt.figure()
    plt.hist(map(len, mathRes))
    plt.show()

if __name__ == "__main__":
    # simpleExample()
    # timings()
    c_elegans()
    # astroph()

