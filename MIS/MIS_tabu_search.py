from numpy.random import choice
from random import randrange
import rustworkx as rx

from .MIS_heuristic import MIS_heuristic


def f(S):
    return len(S)


def updateV(V, Vk):
    V.update(Vk)


def updateT(T, itr):
    _T = T.copy()
    for t in T:
        if t[1] == itr:
            _T.remove(t)
    return _T


def get_Vk(G, S, k, method=lambda x, y: x == y):
    node_indexes = list(G.node_indexes())
    V = set()

    for v in node_indexes:
        v_neighbors = set(G.neighbors(v))
        v_neighbors_in_S = v_neighbors.intersection(S)
        if v not in S and method(len(v_neighbors_in_S), k):
            V.add((v, tuple(v_neighbors_in_S)))

    return V


def diversification_move(G, V, S, T):
    _S = S.copy()
    _T = T.copy()

    if len(V["V1"]) < len(V["V2"]) + len(V["V>2"]):
        Vk = V["V>2"]
    else:
        possible_Vk = ["V2", "V>2"]
        Vk = V[choice(possible_Vk, 1, p=[0.5, 0.5])[0]]

    by_best_diversifying_degree = sorted(
        Vk, key=lambda v: len(set(G.neighbors(v[0])).difference(S)))

    if (len(by_best_diversifying_degree) > 0):
        _S.add(by_best_diversifying_degree[0][0])
        removed_verteces = set(by_best_diversifying_degree[0][1])
        _S = _S.difference(removed_verteces)

        _T = T.union({(removed_vertex, 7)
                     for removed_vertex in removed_verteces})

    V2 = {'V2': get_Vk(G, S, 2)}
    V_gt_2 = {'V>2': get_Vk(G, S, 2, lambda x, y: x > 2)}

    updateV(V, V2)
    updateV(V, V_gt_2)

    return _S, _T


def intensification_move(G, V, S, k, T, itr):
    """
    Funcion que intercambio un (1) vertice no parte de la solucion S por sus k vertices
    vecinos en S

    :param k: numero de vertices en la solucion vecinos al vertice no solucion a intercambiar. k >= 0
    :param S: solucion actual
    :return: solucion con un movimiento realizado
    """

    V0, V1, V2 = V["V0"], V["V1"], V["V2"]
    V_gt_2 = V["V>2"]
    tt = 0
    _S = S.copy()
    _T = T.copy()

    if k == 0:
        _S.add(choice([v[0] for v in V0]))
    else:
        expand_degree = {}
        for v in V1:
            u = v[1][0]
            expand_degree[u] = 1 if expand_degree.get(
                u, None) is None else expand_degree[u] + 1
        expand_degree = dict(
            sorted(expand_degree.items(), key=lambda item: item[1]))

        if len(V1) > len(V2) + len(V_gt_2):
            _V1 = V1.copy()
            for v in V1:
                u = v[1][0]
                if expand_degree[u] == 1:
                    _V1.remove(v)
                    del expand_degree[u]
            tt = 10 + randrange(len(V1))
            V1 = _V1
        else:
            tt = len(V1)

        _V1 = set()
        max_expand_degree = next(iter(expand_degree.values()))

        for v in V1:
            u = v[1][0]
            if expand_degree[u] == max_expand_degree:
                _V1.add(v)

        if len(_V1) == 1:
            v1 = list(V1)[0]
            _S.add(v1[0])
            removed_verteces = set(v1[1])
        else:
            by_best_diversifying_degree = sorted(
                _V1, key=lambda v: len(set(G.neighbors(v[0])).difference(S)))

            if (len(by_best_diversifying_degree) > 0):
                _S.add(by_best_diversifying_degree[0][0])
                removed_verteces = set(by_best_diversifying_degree[0][1])
            else:
                removed_verteces = set()

        _S = _S.difference(removed_verteces)
        _T = T.union({(removed_vertex, itr + tt)
                     for removed_vertex in removed_verteces})

    V0_1 = {'V%s' % (i): get_Vk(G, _S, i) for i in range(2)}
    updateV(V, V0_1)

    return _S, _T


def check_in_T(Vk, T):
    _Vk = Vk.copy()
    for v in Vk:
        for t in T:
            if v[0] == t[0]:
                _Vk.remove(v)

    return _Vk


def elegible_intensification_move(V, T):
    _V0 = check_in_T(V["V0"], T)
    if len(_V0) > 0:
        updateV(V, {"V0": _V0})
        return True, 0

    _V1 = check_in_T(V["V1"], T)
    if len(_V1) > 0:
        updateV(V, {"V1": _V1})
        return True, 1

    return False, None


def MIS_tabu_search(G, max_iter=10):
    """
    Busqueda tabu para encontrar el conjunto maximo independiente de un grafo G.

    :param G: grafo G
    :param max_iter: numero maximo de iteraciones a ejecutar
    :return: indices del grafo que conforman un conjunto independiente maximo
    """
    # Solucion inicial
    S0 = MIS_heuristic(G)

    # Mejor solucion actual
    S = set(S0)

    # Tamano del la mejor solucion
    best_f = f(S)

    # Inicializamos la lista tabu
    T = set()

    V0_2 = {'V%s' % (i): get_Vk(G, S, i) for i in range(3)}
    V_gt_2 = {'V>2': get_Vk(G, S, 2, lambda x, y: x > 2)}

    V = {}
    updateV(V, V0_2)
    updateV(V, V_gt_2)

    for itr in range(max_iter):
        elegible_intensification, k = elegible_intensification_move(V, T)

        if elegible_intensification:

            _S, T = intensification_move(G, V, S, k, T, itr)
            _f = f(_S)

            if best_f <= _f:
                S = _S
                best_f = _f
        else:
            _S, T = diversification_move(G, V, S, T)

        T = updateT(T, itr)
        
    return S
