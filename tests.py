import networkx as nx
from kplex import kplexAlg
import matplotlib.pyplot as plt
from time import time
import pandas as pd
import pickle
from os.path import isfile

def simpleExample():
    print "running simple example"
    G = nx.Graph({
        0: {1,2},
        1: {0, 4,5},
        2: {3,4,0},
        3: {2,4,5},
        4: {1,2,3},
        5: {1,2,3}
    })
    N = len(G.nodes())
    k = 2

    analyzeNetwork(G, k, "simple")
    # kplexes = kplexAlg(G, k)


def timings():
    N_range = [5, 10, 30, 50, 100, 200, 500, 1000, 10000]
    N_range = [5, 10, 30, 50, 100, 200]
    df = pd.DataFrame({}, columns=["N", "time"])
    for N in N_range:
        print N
        G = nx.fast_gnp_random_graph(N, 10./N)
        start_time = time()
        kplexAlg(G, 2)
        run_time = time()-start_time
        print run_time
        df.loc[len(df)] = [N, run_time]

    df = df.set_index("N")
    print df



def analyzeNetwork(G, k=2, filename=None):
    # Get kplexes
    if filename and isfile(filename):
        kplexesMax = pickle.load(open(filename))
    else:
        _, kplexesMax = kplexAlg(G, k, verbose=True)
        if filename:
            pickle.dump(kplexesMax, open(filename, 'wb'))

    print "List of {}-plexes".format(k)
    print kplexesMax

    # get histogram for size of kplex
    kplexSizes = map(len, kplexesMax)
    plt.hist(kplexSizes)
    # get MCC size...


def c_elegans():
    print "Reading worm..."
    G = nx.read_gml("Networks/CelegansNeural/celegansneural.gml")
    print "Done Reading worm. Worm has {} nodes and {} edges".format(len(G.nodes()), len(G.edges()))
    analyzeNetwork(G, 2, "worm")


if __name__ == "__main__":
    # simpleExample()
    # timings()
    c_elegans()

