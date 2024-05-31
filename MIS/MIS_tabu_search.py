from numpy.random import choice
from random import randrange
import rustworkx as rx

from .MIS_heuristic import MIS_heuristic

def f(S):
    """
    Funcion de evaluacion de una posible solucion. Es su tamano pues es lo que buscamos maximizar.
    
    :param S: solucion
    :return: tamano de la solucion
    """
    return len(S)


def updateV(V, Vk):
    """
    Funcion que actualiza una subvecindad Vk de la vecindad V

    :param V: conjunto vecindad
    :param Vk: subconjunto de la vecindad cuyos vertices tiene k vecinos en la solucion
    """
    V.update(Vk)


def updateT(T, itr):
    """
    Funcion que actualiza la lista tabu cuando se cumple que el numero de iteraciones que debe tener un vertice en ella
    desde que fue retirado en un swap de la solucion es igual a la iteracion actual (criterio de aceptación)

    :param T: lista tabu
    :param itr: iteracion actual
    :return: lista tabu actualizada
    """
    _T = T.copy()
    for t in T:
        if t[1] == itr:
            _T.remove(t)
    return _T

def check_in_T(Vk, T):
    """
    Funcion que chequea si un posible vertice en Vk para hacer swap es tabu o no
    
    :para Vk: subconjunto de la vecindad cuyos vertices tiene k vecinos en la solucion
    :param T: lista tabu
    :return: Vk con aquellos vertices que son validos
    """
    _Vk = Vk.copy()
    for v in Vk:
        for t in T:
            if v[0] == t[0]:
                _Vk.discard(v)

    return _Vk

def get_Vk(G, S, k, method=lambda x, y: x == y):
    """
    Funcion que obtiene una subvecindad Vk para k (0, 1, 2, >2) siendo k el numero
    de vertices vecinos que tiene un vertice v en Vk presentes en la solucion S

    :param G: grafo del que queremos el conjunto independiente maximo
    :param S: solucion actual
    :param k: numero de vertices en la solucion vecinos al vertice no solucion a intercambiar. k >= 0
    :param method: metodo que compara el numero de vertices vecinos en S a un v en G que no forme parte de S con k
    :return: subvecindad Vk
    """
    
    node_indexes = list(G.node_indexes())
    V = set()

    for v in node_indexes:
        v_neighbors = set(G.neighbors(v))
        v_neighbors_in_S = v_neighbors.intersection(S)
        if v not in S and method(len(v_neighbors_in_S), k):
            V.add((v, tuple(v_neighbors_in_S)))

    return V

def intensification_move(G, V, S, k, T, itr):
    """
    Funcion que intercambio un (1) vertice no parte de la solucion S por sus k vertices
    vecinos en S

    :param G: grafo del que queremos el conjunto independiente maximo
    :param V: vecindad de S
    :param S: solucion actual
    :param k: numero de vertices en la solucion vecinos al vertice no solucion a intercambiar. 0 <= k < 2
    :param T: lista tabu
    :param itr: iteracion actual
    :return: solucion con un movimiento realizado
    """

    V0, V1, V2 = V["V0"], V["V1"], V["V2"]
    V_gt_2 = V["V>2"]
    tt = 0 # iteraciones que deben pasar para que un vertice sacado de S deje de ser tabu
    _S = S.copy()
    _T = T.copy()

    # Si k es 0, vamos a mejorar S y podemos insertar un vertice random de la subvecindad V0 sin problemas en S
    if k == 0:
        _S.add(choice([v[0] for v in V0]))
    else:
        # Si k no es 0, entonces es 1 y vamos a hacer un intercambio vacado en el grado de expansion de los vertices en S
        # El grado de expansion para un v en S es a cuantos vertices es vecino para aquellos en la subvecindad V1
        expand_degree = {}
        for v in V1:
            u = v[1][0]
            expand_degree[u] = 1 if expand_degree.get(
                u, None) is None else expand_degree[u] + 1
        expand_degree = dict(
            sorted(expand_degree.items(), key=lambda item: item[1]))

        # Si hay más movimientos swap(1,1) que swap(k, 1) (k > 1) (es decir, |V1| > |V2| + |V>2|), 
        # excluimos de V1 cualquier vértice vi tal que su vecino adyacente vj tiene un grado de expansión de 1
        # porque seria un "side-walk" o movimiento lateral y vamos a tratar de evitar hacerlos seguidos. Saco vj de S para meter a vi y el unico vecino que tiene ahora dentro vj es vi
        if len(V1) > len(V2) + len(V_gt_2):
            _V1 = V1.copy()
            for v in V1:
                u = v[1][0]
                if expand_degree[u] == 1:
                    _V1.remove(v)
                    del expand_degree[u]
            # Elegir tt se basa en que cuando hay muchos movimientos laterales 
            # el vértice que acaba de salir de la solución no será aceptado 
            # antes de haber intentado un número de movimientos laterales tan alto como |V1|.
            tt = len(V1)
            V1 = _V1
        else:
            # Si no es un movimiento lateral no hace falta marcarlo tabu por demasiado tiempo.
            tt = 10 + randrange(len(V1))

        # Aplicamos una regla de seleccion tal que en _V1 tomaremos cualquier v en V1 tal que
        # su vecino en S tiene el mayor grado de expansión de todos los consideramos 
        _V1 = set()
        max_expand_degree = next(iter(expand_degree.values()))

        for v in V1:
            u = v[1][0]
            if expand_degree[u] == max_expand_degree:
                _V1.add(v)
                
        # Luego, si _V1 solo tiene un vertice, tomamos ese para el swap(1,1)
        if len(_V1) == 1:
            v1 = list(V1)[0]
            _S.add(v1[0])
            removed_verteces = set(v1[1])
        else:
            # Si no eligiremos el vertices con el mayor grado de diversificacion. Esto es,
            # el vertices en _V1 que mas vecinos tenga en el grafo sin considerar los que estan en S
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

    # Actualizamos la vecindad
    V0_1 = {'V%s' % (i): get_Vk(G, _S, i) for i in range(2)}
    updateV(V, V0_1)

    return _S, _T

def diversification_move(G, V, S, T, itr):
    """
    Funcion que perturba la solucion S por medio de retirar los k vertices vecinos presentes en S
    para un k >= 2. Esto "retorna una peor solucion" por un k - 1

    :param G: grafo del que queremos el conjunto independiente maximo
    :param V: vecindad de S
    :param S: solucion actual
    :param T: lista tabu
    :param itr: iteracion actual
    :return: solucion perturbada
    """
    _S = S.copy()
    _T = T.copy()
    
    # Si |V1| > |V2| + |V>2 |, usamos V>2 para realizar una fuerte
    # perturbación mediante un movimiento swap(k, 1) (k > 2)
    if len(V["V1"]) > len(V["V2"]) + len(V["V>2"]):
        Vk = V["V>2"]
    # Si no se cumple lo anterior, elegimos una perturbacion fuerte o una mas suave (V2) con 
    # la misma probabilidad
    else:
        possible_Vk = ["V2", "V>2"]
        Vk = V[choice(possible_Vk, 1, p=[0.5, 0.5])[0]]
        
    # Luego seleccionamos un vértice elegible v de la subvecindad elegida con el mayor grado de diversidad.
    by_best_diversifying_degree = sorted(
        Vk, key=lambda v: len(set(G.neighbors(v[0])).difference(S)))

    if (len(by_best_diversifying_degree) > 0):
        _S.add(by_best_diversifying_degree[0][0])
        removed_verteces = set(by_best_diversifying_degree[0][1])
        _S = _S.difference(removed_verteces)

        # Los vertices retirados podran usarse luego de tan solo siete (7) iteraciones
        _T = T.union({(removed_vertex, itr + 7)
                     for removed_vertex in removed_verteces})

    # Actualizamos la vecindad
    V2 = {'V2': get_Vk(G, S, 2)}
    V_gt_2 = {'V>2': get_Vk(G, S, 2, lambda x, y: x > 2)}

    updateV(V, V2)
    updateV(V, V_gt_2)

    return _S, _T

def elegible_intensification_move(V, T):
    """
    Funcion que chequea si hay un movimiento de intensificacion posible en la vecindad.
    En otras palabras, si podemos hacer swap(k, 1) para k = 0, 1
    
    :para V: vecindad de la busqueda tabu
    :param T: lista tabu
    :return: si existe algun movimiento de itensificacion y, si hay, el k correspondiente
    """
    # Verificamos si la subvecindad V0 tiene vertices y esos no estan en T; es decir, no son tabu
    _V0 = check_in_T(V["V0"], T)
    if len(_V0) > 0:
        updateV(V, {"V0": _V0})
        return True, 0

    # Verificamos si la subvecindad V1 tiene vertices y esos no estan en T; es decir, no son tabu
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

    # Mejor solucion hasta el momento
    S = set(S0)
    
    # Solucion actual
    _S = S.copy()
    
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
        
        # Chequeamos si podemos intensificar
        elegible_intensification, k = elegible_intensification_move(V, T)

        if elegible_intensification:

            _S, T = intensification_move(G, V, _S, k, T, itr)
            _f = f(_S)

            # Si intensificamos y el resultado es mejor acorde a la funcion de evaluacion
            if best_f < _f:
                S = _S.copy()
                best_f = _f
        else:
            # Cuando la solución actual no puede mejorarse mediante un swap(0,1) 
            # o modificarse mediante un swap(1,1), 
            # el procedimiento de búsqueda queda atrapado en un óptimo local
            # vamos a perturbar la solucion actual
            _S, T = diversification_move(G, V, _S, T, itr)

        T = updateT(T, itr)
        
    return list(S)
