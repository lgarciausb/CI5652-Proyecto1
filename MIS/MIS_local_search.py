import rustworkx as rx
from random import choice
from itertools import combinations
from .MIS_exact import MIS_exact

def MIS_local_search(G, S, k=1):
    if k <= 0 and k >= len(S):
        return S
    kS = set(combinations(S, k))
    node_indexes = G.node_indices()
    for k_tuple in kS:
        V = set(S).difference(set(k_tuple))
        _G = G.copy()
        for v in V:
            v_neighbors = G.neighbors(v)
            _G.remove_nodes_from(v_neighbors)
            _G.remove_node(v)
        newS = set(MIS_exact(_G))

        if len(newS) > k:
            S = list(V.union(newS))
            MIS_local_search(G, S, k)
    return S