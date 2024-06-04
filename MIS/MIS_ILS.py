from operator import itemgetter
from numpy.random import choice
from heapq import nlargest
from random import randrange
import rustworkx as rx

from .MIS_local_search import MIS_local_search
from .MIS_heuristic import MIS_heuristic


def force(G, S, k, history, itr):
    """
    Perturbacion que consta de agregar k vertices randoms pertenecientes al grafo G pero
    que no formen parte de la solucion S y, si sus vecinos forman parte de S, retirarlos de S

    :param G: grafo G
    :param S: solucion actual
    :return: solucion perturbada
    """ 
    _G = G.copy()
    _S = S.copy()
    
    for v in S:
        # Grafo con vertices que no formen parte de la solucion actual
        _G.remove_node(v)
    node_indexes = list(_G.node_indexes())
    
    if k == 1:
        
        chosen_v = choice(node_indexes)
        history[chosen_v] = itr
        
        # Borramos de la solucion los vecinos del elegido
        chosen_v_neighbors = G.neighbors(chosen_v)
        for s in S:
            if s in chosen_v_neighbors:
                _S.discard(s)
        _S.add(chosen_v)
    else:
        
        # Seleccionamos aleatoriamente k vertices que tengan al menos un vecino en S y no esten en S
        possible_k = []
        
        for v in node_indexes:
            for s in S:
                if v in G.neighbors(s):
                    possible_k.append(v)
        
        # Seleccionamos 4 vertices de entre los que tienen al menos un vecino en S
        possible_k = choice(possible_k, 4)
                
        # Elegimos a alguno de los que lleven menos iteraciones desde que estuvieron en S (si estuvieron alguna vez)
        last_itr_possible_k = {v: history.get(v, 0) for v in possible_k}
        chosen_v = min(last_itr_possible_k, key=last_itr_possible_k.get)
                
        # Queremos incluir tambien aquellos que esten a distancia dos (2) del vertice elegido y no esten en S
        distances_from_chosen_v = rx.distance_matrix(G)[chosen_v]
        distance_2_from_chosen_v = [u for u, d in enumerate(distances_from_chosen_v) if d == 2 and u not in S]
        
        # Elegimos k - 1 vertices de los que esten a dos de distancia del primer vertice elegido (hay al menos un vertice que impide que sean vecinos), si lo hay
        # Si no hay suficientes vertices para sumar k - 1, entonces solo aquellos que cumplan incluso si son menos.
        chosen = set()
        if len(distance_2_from_chosen_v) > 0:
            chosen = set(choice(distance_2_from_chosen_v, k - 1))
        chosen.add(chosen_v)
        
        # Borramos de la solucion los vecinos de los elegidos
        for v in chosen:
            for s in S:
                if s in G.neighbors(v):
                    _S.discard(s)
            _S.add(v)
            history[v] = itr
            S = _S.copy()

    return _S


def acceptanceCondition(S, _S, i, itr):
    """
    Condicion de aceptacion para decidir si la solucion perturbada debe ser la actual solucion

    :param S: solucion actual
    :param _S: solucion perturbada
    :param i: iteracion a la que debe llegar sin cambios para aceptar una solucion perturbada que no mejore la actual
    :param itr: iteracion actual
    :return: solucion actual, mejor solucion, iteracion i sin cambios
    """ 
    # Si la solucion perturbada es mejor que la actual
    if len(S) < len(_S):
        S = _S.copy()
        
        # No se puede aceptar una solucion perturbada que sea peor a la actual por |S| iteraciones
        # Intuitivamente, cuanto más lejos esté _S de S, menos probable es que el algoritmo establezca S = _S
        i = itr + len(S)
            
    # Si pasaron |S| iteraciones desde que se llego a la solucion actual por medio de una perturbada mejor,
    # podemos aceptar una solucion perturbada que no sea mejor a la actual que se tenia
    elif itr == i:
        S = _S.copy()

    return S, i


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

    # Mejor solucion actual
    S = set(MIS_local_search(G, S0, len(S0) - 1))
    
    # i es una especie de contador que nos indicara cuando podemos aceptar un
    # resultado de la perturbacion que sea peor a la solucion actual
    i = 0
    
    itr = 0
    
    # Almacena un vertice y la ultima vez que formo parte de la solucion una vez que es forzado
    history = {}
    
    # El criterio de parada es un numero maximo de iteraciones definidos o, en su lugar, la cantidad de
    # arcos del grafo
    while itr < (max_iter if max_iter is not None else num_edges):
        # Elegimos un k para la perturbacion tal que si estamos en la primera iteracion
        # k = 1 siempre y, si no, con una probabilidad pequena de 1 / (2 * len(S)) elegimos un k mayor a 1.
        # La mayor parte del tiempo k == 1
        a = randrange(1, 2*len(S))
        k = 1 if a != 1 else i + 1
        # Perturbacion de la solucion actual
        _S = force(G, S, k, history, itr)
        
        # Local search sobre el resultado de la perturbacion
        _S = set(MIS_local_search(G, _S, len(_S) - 1))

        # Definimos si el resultado de la perturbacion es aceptado como nuevo maximum independent set
        S, i = acceptanceCondition(S, _S, i, itr)
        itr += 1
    return list(S)

