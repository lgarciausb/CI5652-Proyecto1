from operator import itemgetter
from numpy.random import choice
from heapq import nlargest
from random import randrange
import rustworkx as rx

from .MIS_local_search import MIS_local_search
from .MIS_heuristic import MIS_heuristic


def force(G, S, k):
    """
    Perturbacion que consta de agregar k vertices randoms pertenecientes al grafo G pero
    que no formen parte de la solucion S y, si sus vecinos forman parte de S, retirarlos de S

    :param G: grafo G
    :param S: solucion actual
    :return: solucion perturbada
    """ 
    _G = G.copy()
    
    for v in S:
        # Grafo con vertices que no formen parte de la solucion actual
        _G.remove_node(v)
    node_indexes = list(_G.node_indexes())
    
    kForceInsert = set()
    
    if len(node_indexes) > 0:
        kForceInsert = set(choice(node_indexes, k))
        
    # Si uno de los nodos a insertar tiene un vecino en la solucion actual, 
    # sacamos el nodo vecino e insertamos el nuevo
    _S = S.copy()
    for v in kForceInsert:
        for s in S:
            if v in G.neighbors(s):
                _S.discard(s)

    return _S.union(kForceInsert)


def acceptanceCondition(S, _S, best_S, i, itr):
    """
    Condicion de aceptacion para decidir si la solucion perturbada debe ser la actual solucion

    :param S: solucion actual
    :param _S: solucion perturbada
    :param best_S: mejor solucion
    :param i: iteracion a la que debe llegar sin cambios para aceptar una solucion perturbada que no mejore la actual
    :param itr: iteracion actual
    :return: solucion actual, mejor solucion, iteracion i sin cambios
    """ 
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


def MIS_ILS(G, max_iter=None):
    """
    Busqueda local iterativa para encontrar el conjunto maximo independiente de un grafo G.

    :param G: grafo G
    :param max_iter: numero maximo de iteraciones a ejecutar
    :return: indices del grafo que conforman un conjunto independiente maximo
    """ 
    num_edges = G.num_edges()

    # Solucion inicial
    S0 = MIS_heuristic(G)

    # Solucion actual
    S = set(MIS_local_search(G, S0, len(S0) - 1))

    # Mejor solucion hasta el momento
    best_S = S.copy()

    # i es una especie de contador que nos indicara cuando podemos aceptar un
    # resultado de la perturbacion que sea pero a la solucion actual
    i = 0
    
    itr = 0
    # El criterio de parada es un numero maximo de iteraciones definidos o, en su lugar, la cantidad de
    # arcos del grafo
    while itr < (max_iter if max_iter is not None else num_edges):
        # Elegimos un k para la perturbacion tal que si estamos en la primera iteracion
        # k = 1 siempre y, si no, con una probabilidad pequena de 1 / (2 * len(S)) elegimos un k mayor a 1.
        # La mayor parte del tiempo k == 1
        num_left_verteces = G.subgraph(list(set(G.node_indexes()).difference(S))).num_nodes()       
        possible_k = [1, randrange(2, num_left_verteces) if num_left_verteces > 2 else 1]
        probability_bigger_k = 1 / (2 * len(S))
        k = choice(possible_k, 1, p=[
                   1 - probability_bigger_k, probability_bigger_k])

        # Perturbacion de la solucion actual
        _S = force(G, S, k)

        # Local search sobre el resultado de la perturbacion
        _S = set(MIS_local_search(G, _S, len(_S) - 1))

        # Definimos si el resultado de la perturbacion es aceptado como nuevo maximum independent set
        S, best_S, i = acceptanceCondition(S, _S, best_S, i, itr)
        itr += 1
    return list(best_S)

