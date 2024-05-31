import rustworkx as rx
from random import choice
from itertools import combinations
from .MIS_exact import MIS_exact

def MIS_local_search(G, S, k=1):
    """
    Busqueda local para encontrar el conjunto maximo independiente de un grafo G haciendo k-exchanges sobre
    un conjunto independiente del grafo dado.

    :param G: grafo G
    :param S: conjunto independiente de G
    :param k: cuanto exchanges se van a realizar
    :return: indices del grafo que conforman un conjunto independiente maximo
    """ 
    _G = G.copy()
    _S = S.copy()
    if k <= 0 and k >= len(S):
        return S
    kS = set(combinations(S, k))
    node_indexes = G.node_indices()
    for k_tuple in kS:
        V = set(S).difference(set(k_tuple))
        for v in V:
            v_neighbors = G.neighbors(v)
            _G.remove_nodes_from(v_neighbors)
            _G.remove_node(v)
        newS = set(MIS_exact(_G))

        if len(newS) > k:
            _S = list(V.union(newS))
            MIS_local_search(G, _S, k)
    return _S
