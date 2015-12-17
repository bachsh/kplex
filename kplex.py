__author__ = 'aaminov'


import networkx as nx
import matplotlib.pyplot as plt
from copy import copy
from time import sleep

ROOT = (-1, -1, 0, 0, 0)
TREE_NODE_TEMPLATE = (0, # degree
                      -1, # node
                      0, # global index
                      0, # no. of failed neighbors (no. of nodes up the tree that this node is not connected to)
                      0, # 1 if node not connected to its parent
                      )
LEFT_SIBLINGS = False

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


def initKplexTree(G):
    tree = nx.DiGraph()
    tree.add_node(ROOT)
    for v in G.nodes():
        newHead = (0, v, 0, 0, 0)
        tree.add_node(newHead)
        tree.add_edge(ROOT, newHead)
    return tree, tree.successors(ROOT)


# Creates an auxiliary tree used to find k-plexes
# G - Given graph
# T - empty tree
# candidates - all nodes
def kplexTree(G, T, leftSiblings, rightSiblings, k, parent = ROOT, degree = -1, ind = 0):
    if not LEFT_SIBLINGS:
        leftSiblings = set()
    pNeighbors = G.neighbors(parent[1])
    for sib in rightSiblings:
        vSib = sib[1]
        notConnectedToSib = vSib not in pNeighbors
        score = sib[3] + notConnectedToSib
        parentScore = parent[3] + notConnectedToSib
        # print sib, parent, T.predecessors(parent)[0]
        gParentScore = T.predecessors(parent)[0][3] + sib[4] + parent[4]
        if score < k and parentScore < k and gParentScore < k:
            ind += 1
            newLeaf = (degree+1, vSib, ind, score, notConnectedToSib)
            T.add_node(newLeaf)
            T.add_edge(parent, newLeaf)

    newRightSiblings = set(filter(lambda x: x[2] > 0, T.successors(parent)))
    parentIsLeaf = len(newRightSiblings) == 0
    for sib in leftSiblings:
        vSib = sib[1]
        notConnectedToSib = vSib not in pNeighbors
        score = sib[3] + notConnectedToSib
        parentScore = parent[3] + notConnectedToSib
        if score < k and parentScore < k:
            ind += 1
            if sib[2] < 0:
                T.add_edge(parent, sib)
            else:
                newLeaf = (degree+1, vSib, -ind, score)
                T.add_node(newLeaf)
                T.add_edge(parent, newLeaf)
            if parentIsLeaf:
                return ind


    if LEFT_SIBLINGS:
        allSiblings = T.successors(parent)
        newLeftSiblings = set(filter(lambda x: x[2] < 0, allSiblings))
    # print "all", allSiblings
    # print "right", newRightSiblings
    # print "left", newLeftSiblings
    while len(newRightSiblings) > 0:
        sib = newRightSiblings.pop()
        if LEFT_SIBLINGS:
            ind = kplexTree(G, T, newLeftSiblings, newRightSiblings, k, sib, degree+1, ind)
            newLeftSiblings.add(sib)
        else:
            ind = kplexTree(G, T, set(), newRightSiblings, k, sib, degree+1, ind)
    return ind


def kplexFromLeaf(T, leaf):
    if leaf == ROOT:
        return set()
    # print leaf
    res = kplexFromLeaf(T, T.predecessors(leaf)[0])
    res.add(leaf[1])
    return res


# Extract k-plexes from the tree generated by the function kplexTree
def kplexesFromTree(T, node = ROOT):
    succ = filter(lambda x: x[2]>=0, T.successors(node))
    kplex = kplexFromLeaf(T, node)
    kplexes = [kplex]
    for v in succ:
        kplexes.extend(kplexesFromTree(T, v))
    return kplexes

# Extract k-plexes from the tree generated by the function kplexTree
def kplexesFromLeaves(T, node = ROOT):
    succ = filter(lambda x: x[2]>=0, T.successors(node))
    if succ == []:
        if len(T.successors(node)) == 0:
            kplex = kplexFromLeaf(T, node)
            return [kplex]
        return []
    kplexes = []
    for v in succ:
        kplexes.extend(kplexesFromLeaves(T, v))
    return kplexes


def getMaximalSets(sets):
    if True: # Remove all 2-vertices
        sets = filter(lambda x: len(x)>2, sets)
    maxSize = max(map(len, sets))
    print "max kplex size", maxSize
    setsBySize = dict()
    largerSet = (filter(lambda x: len(x) == 3, sets))
    for i in range(3, maxSize):
        candidates = largerSet
        largerSet = (filter(lambda x: len(x) == i+1, sets))
        setsBySize[i] = []
        for s in candidates:
            found = False
            for s2 in largerSet:
                if s.issubset(s2):
                    found = True
                    break
            if not found:
                setsBySize[i].append(s)
    setsBySize[maxSize] = largerSet
    maxSets = []
    for i in range(3, maxSize+1):
        maxSets.extend(setsBySize[i])
    return maxSets


def connected(G, v, subset):
    neighbors = G.neighbors(v)
    for node in subset:
        if node in neighbors:
            return True
    return False

# Function: FindAllMaxKplex (inputCompsub, inputCandidate, inputNot)
def FindAllMaxKplex(G, k, kplexesList, inputCompsub, inputCompsubCount, inputCandidate, inputCandidateCount, inputNotset, inputNotsetCount):
# 6: Copy inputCompsub to compsub. Copy inputCandidate to candidate. Copy inputNot to not;
    compsub = copy(inputCompsub)
    compsubCount = copy(inputCompsubCount)
    candidate = copy(inputCandidate)
    candidateCount = copy(inputCandidateCount)
    notset = copy(inputNotset)
    notsetCount = copy(inputNotsetCount)

# 7: Select a vertex v in connected_candidate of inputCandidate in lexicographic order;
    if len(compsub) == 0:
        for node in inputCandidate:
            v = node
            break
    else:
        for node in inputCandidate:
            if connected(G, node, compsub):
                v = node
                break
# 8: Move v to compsub and Update the counters of the vertices in compsub;
    try:
        vNeighbors = set(G.neighbors(v))
    except:
        return None
    for node in compsub:
        if node not in vNeighbors:
            compsubCount[node] += 1
    compsubCount[v] = len(compsub) - len(vNeighbors & compsub)
    compsub.add(v)
    candidate.remove(v)
# 9: if there are n critical vertices in compsub (n > 0):
# 10:   Compute the intersection C of the neighborhoods of the n critical vertices and Remove all the vertices in candidate and not which are not in C;
    criticalNodes = filter(lambda node: compsubCount[node] == k-1, compsub)
    if len(criticalNodes) > 0:
        C = set(G.nodes())
        for node in criticalNodes:
            C &= set(G.neighbors(node))
        candidate &= C
        notset &= C

# 11: Update the counters of the vertices in candidate and not and Remove the vertices of candidate and not if the vertices
# can not expand compsub (the counter is greater than k-1);
    disqualCandidate = set()
    for node in candidate:
        if node not in vNeighbors:
            candidateCount[node] += 1
            if candidateCount[node] > k-1:
                disqualCandidate.add(node)
    candidate -= disqualCandidate
    disqualNotset = set()
    for node in notset:
        if node not in vNeighbors:
            notsetCount[node] += 1
            if notsetCount[node] > k-1:
                disqualNotset.add(node)
    notset -= disqualNotset

# 12: Generate connected_candidate of candidate and connected_not of not;
    connectedCandidate = set()
    for node in candidate:
        if connected(G, node, compsub):
            connectedCandidate.add(node)
    connectedNot = set()
    for node in notset:
        if connected(G, node, compsub):
            connectedNot.add(node)
# 13: if connected_candidate and connected_not are empty:
    if len(connectedCandidate) == 0 and len(connectedNot) == 0:
# 14:    compsub is a maximal k-plex, Return v;
        kplexesList.append(compsub)
        return v
# 15: if connected_candidate is empty and connected_not is not empty:
    if len(connectedCandidate) == 0:
# 16:   Return that there are no vertices which can expand compsub;
        return None
# 17: if connected_candidate and connected_not is not empty:
# 18: while there are vertices in candidate:
    while len(candidate) > 0:
# 19:   Call FindAllMaxKplex(compsub,candidate,not);
        v1 = FindAllMaxKplex(G, k, kplexesList, compsub, compsubCount, candidate, candidateCount, notset, notsetCount)
        if v1 == None:
            return v
        candidate.remove(v1)
# 20:   Move the used vertex to not upon the return;
        notset.add(v1)
        notsetCount[v1] = candidateCount[v1]
# 21: endwhile;
# 22: Return v;
    return v




def kplexAlg(G, k, verbose=False, method=None):
    if method == None:
        method = "wu"
    if method == "tree":
        if verbose:
            print "Building auxiliary tree..."
        tree, rightSiblings = initKplexTree(G)
        rightSiblings = set(rightSiblings)
        leftSiblings = set()
        ind = 0
        while len(rightSiblings) > 0:
            head = rightSiblings.pop()
            ind = kplexTree(G, tree, leftSiblings, rightSiblings, k, head, 0, ind)
            leftSiblings.add(head)
            # print "done with {}".format(head)
        if verbose:
            print "Done Building auxiliary tree"
            print "Reading all kplexes..."

        # print "Writing to file"
        # nx.write_dot(tree, "tree.dot")

        kplexFull = kplexesFromTree(tree)
        kplexPartial = kplexesFromLeaves(tree)
        if verbose:
            print "Done Reading all kplexes"
            print "Getting maximal kplexes..."
        # kplexMax = kplexFull
        kplexMax = getMaximalSets(kplexPartial)
        # kplexMax = getMaximalSets(kplexFull)
        if verbose:
            print "Done Getting maximal kplexes"
        return kplexFull, kplexMax

    if method == "wu": # Pemp algorithm by Wu and Pei
        compsub = set()
        candidate = set(G.nodes())
        notset = set()
        candidateCount = {x:0 for x in candidate}
        kplexMax = []
        notset = set()
        notsetCount = {x:0 for x in candidate}
        while len(candidate) > 0:
            v = FindAllMaxKplex(G, k, kplexMax, set(), {}, candidate, candidateCount, notset, notsetCount)
            print v
            if v == None:
                break
            candidate.remove(v)
            notset.add(v)
        return kplexMax, kplexMax



if __name__ == "__main__":

    networkFile = "smallExamples/net20_30.net"
    # G = nx.read_pajek(networkFile)
    # G = nx.fast_gnp_random_graph(20, 0.2)

    G = nx.Graph({
        0: {1,2},
        1: {0,2,4,5},
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

    k = 2
    kplexes, kplexesMax = kplexAlg(G, k)
    print "List of {}-plexes".format(k)
    print kplexes
    print kplexesMax
    plt.figure()

    raw_input("Press <Enter> to continue")

