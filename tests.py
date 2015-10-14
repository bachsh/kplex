import networkx as nx
from kplex import kplexAlg
import matplotlib.pyplot as plt
from time import time
import pandas as pd

def simpleExample():
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
    kplexes = kplexAlg(G, k)
    print "List of {}-plexes".format(k)
    print kplexes


def timings():
    N_range = [5, 10, 30, 50, 100, 200, 500]
    # N_range = [5,10]
    df = pd.DataFrame({}, columns=["N", "time"])
    for N in N_range:
        print N
        G = nx.fast_gnp_random_graph(N, 0.3)
        start_time = time()
        kplexAlg(G, 2)
        run_time = time()-start_time
        print run_time
        df.loc[len(df)] = [N, run_time]

    df = df.set_index("N")
    print df



if __name__ == "__main__":
    # simpleExample()
    timings()

