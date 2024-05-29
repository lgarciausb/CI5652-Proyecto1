from operator import itemgetter
from numpy.random import choice
from heapq import nlargest
import rustworkx as rx

from .MIS_local_search import MIS_local_search
from .MIS_heuristic import MIS_heuristic


def force(G, S, k):
    _G = G.copy()

    for v in S:
        # Los vertices de G que no son vecinos a un vertices en S
        _G.neighbors(v)
        _G.remove_nodes_from(list(v_neighbors))

        # Grafo con vertices que no formen parte de la solucion actual
        _G.remove_node(v)
    node_indexes = list(_G.node_indexes())

    kForceInsert = set(choice(node_indexes, k))

    return _S.union(kForceInsert)


def acceptanceCondition(S, _S, best_S, i, itr):
    # Si la solucion perturbada es mejor que la actual
    if len(S) < len(_S):
        S = _S
        
        # No se puede aceptar una solucion perturbada que sea peor a la actual por |S| iteraciones
        # Intuitivamente, cuanto más lejos esté _S de S y best_S, menos probable es que el algoritmo establezca S = _S
        i = itr + len(S)
        if len(best_S) < len(S):
            best_S = S
            
    # Si pasaron |S| iteraciones desde que se llego a la solucion actual por medio de una perturbada mejor,
    # podemos aceptar una solucion perturbada que no sea mejor a la actual que se tenia
    elif itr == i:
        S = _S

    return S, best_S, i


def MIS_ILS(G, max_inter=None):
    num_edges = G.num_edges()

    # Solucion inicial
    S0 = MIS_heuristic(G)

    # Solucion actual
    S = set(MIS_local_search(G, S0, len(S0) - 1))

    # Mejor solucion hasta el momento
    best_S = S

    # i es una especie de contador que nos indicara cuando podemos aceptar un
    # resultado de la perturbacion que sea pero a la solucion actual
    i = 0
    
    itr = 0
    # El criterio de parada es un numero maximo de iteraciones definidos o, en su lugar, la cantidad de
    # arcos del grafo
    while itr < (max_inter if max_inter is not None else num_edges):
        # Elegimos un k para la perturbacion siento que si estamos en la primera iteracion
        # k = 1 siempre y, si no, con una probabilidad pequena de 1 / (2 * len(S)) elegimos un k mayor a 1.
        # La mayor parte del tiempo k == 1
        possible_k = [1, i + 1]
        probability_bigger_k = 1 / (2 * len(S))
        k = choice(possible_k, 1, p=[
                   1 - probability_bigger_k, probability_bigger_k])

        # Perturbacion de la solucion actual
        _S = force(G, S, k, history)

        # Local search sobre el resultado de la perturbacion
        _S = MIS_local_search(G, _S, len(_S) - 1)

        # Definimos si el resultado de la perturbacion es aceptado como nuevo maximum independent set
        S, best_S, i = acceptanceCondition(S, _S, best_S, history)
        itr += 1
    return list(best_S)