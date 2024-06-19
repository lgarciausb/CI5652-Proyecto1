import rustworkx as rx

from numpy.random import choice


def heuristic(G, v):
    """
    Valor de la heuristica del nodo v para un grafo dado G siendo esta la informacion local

    :param G: grafo a considerar que contiene a v
    :param v: vertice al que le queremos calcular su heuristica
    :return: valor de la heuristica
    """

    # Por la definición del conjunto independiente si el vértice tiene un grado alto, entonces
    # tiene menos posibilidades de estar incluido en un conjunto independiente máximo. Pero, ademas
    # nos interesa que los vecinos de los vecinos del vertice sean muchos,
    # con pocos lados conectandolos 
    neighbors = set(G.neighbors(v))

    neighbors_of_neighbors = set()
    for u in neighbors:
        neighbors_of_neighbors = neighbors_of_neighbors.union(
            set(G.neighbors(u)))

    sum_degree_neighbors_of_neighbors = sum(
        [G.degree(u) for u in neighbors_of_neighbors])
    sum_degree_squares_neighbors_of_neighbors = sum(
        [pow(G.degree(u), 2) for u in neighbors_of_neighbors])

    # El 1 es incluido para evitar ceros.
    return (len(neighbors_of_neighbors) + 1) * (sum_degree_squares_neighbors_of_neighbors + 1) / ((1/2 * sum_degree_neighbors_of_neighbors) + 1)


def probability(complement_Sk, v_heuristic, pheromone_trail, alpha, beta):
    """
    Probabilidad de seleccionar un v que no este en el conjunto solucion de la hormiga k sino en su complemento

    :param complement_Sk: complemento de la solucion de la hormiga
    :param v_heuristic: tupla del (v, heuristic) del nodo considerado donde v es el nodo, heuristic es el valor de su heuristica en el grafo considerado por la hormiga
    :param pheromone_trail: valor de la feromona en el nivel anterior.
    :param alpha: relevancia de la informacion flobal (el rastro de la feromona). Debe estar entre 0 y 1
    :param beta: relevancia de la informacion local (heuristica). Debe estar entre 0 y 1
    :return: probabilidad de seleccionas v en v_heuristic
    """
    sum_trail_heuristic = sum(
        [pow(pheromone_trail[u[0]], alpha) * pow(u[1], beta) for u in complement_Sk])
    return pow(pheromone_trail[v_heuristic[0]], alpha) * pow(v_heuristic[1], beta) / sum_trail_heuristic


def update_pheromones(S, node_indexes, pheromone_trail, p, Q):
    """
    Funcion que actualiza la feromona en cada nivel.

    :param S: mejor conjunto solucion hasta el momento
    :param node_indexes: lista de los nodos del grafo original
    :param pheromone_trail: valor de la feromona en el nivel anterior.
    :param Q: valor por el que multiplicar el tamano del conjunto actual para actualizar la feromona si el nodo esta en el conjunto.
    :param p: Tasa de evaporacion de la feromona. Debe estar entre 0 y 1
    """
    for node in node_indexes:
        pheromone_trail[node] = (1 - p) * pheromone_trail[node]

        if node in S:
            pheromone_trail[node] += Q * len(S)


def MIS_ACO(G, max_iter=10, number_of_ants=10, alpha=0.5, beta=0.5, Q=0.05, p=0.8, initial_pheromone=1.0):
    """
    Optimizacion de colonia de hormigas para encontrar el conjunto maximo independiente de un grafo G.

    :param G: grafo G
    :param max_iter: maximo numero de iteraciones 
    :param number_of_ants: numero de hormigas en la colonia
    :param alpha: relevancia de la informacion flobal (el rastro de la feromona). Debe estar entre 0 y 1
    :param beta: relevancia de la informacion local (heuristica). Debe estar entre 0 y 1
    :param Q: valor por el que multiplicar el tamano del conjunto actual para actualizar la feromona si el nodo esta en el conjunto.
    :param p: Tasa de evaporacion de la feromona. Debe estar entre 0 y 1
    :param initial_pheromone: valor inicial de la feromona.
    :return: indices del grafo que conforman un conjunto independiente maximo
    """
    node_indexes = list(G.node_indexes())
    # Rastro de la feromona
    pheromone_trail = [initial_pheromone for _ in range(G.num_nodes())]

    S = set()
    _G = G.copy()

    # Criterio de parada
    for _ in range(max_iter):

        # Por cada hormiga
        for k in range(number_of_ants):

            # Punto de partida random siendo Sk la solucion encontrada por esta hormiga
            Sk = set()
            v = choice(node_indexes)
            Sk.add(v)

            # Queremos todos los nodos que no esten en el Sk considerado ni sean vecinos del mismo
            neighbors = list(_G.neighbors(v))
            _G.remove_node(v)
            _G.remove_nodes_from(neighbors)

            # El complemento de la solucion hasta el momento son los vertices del grafo anterior
            # (vertices que no esten en la solucion ni sean vecinos a los vertices en la misma), lo guardamos con
            # su valor de la heuristica
            complement_Sk = set()
            _node_indexes = _G.node_indexes()
            for n in _node_indexes:
                complement_Sk.add((n, heuristic(_G, n)))

            # Mientras hayan vertices que no sean vecinos de los que estan en Sk
            while (len(complement_Sk) > 0):
                list_complement_Sk = list(complement_Sk)
                # Elegimos uno con cierta probabilidad
                selected_v = list_complement_Sk[choice(len(list_complement_Sk), 1, [probability(
                    complement_Sk, v, pheromone_trail, alpha, beta) for v in complement_Sk])[0]]

                # Actualizamos el complemento y el Sk
                complement_Sk.remove(selected_v)

                selected_v_neighbors = _G.neighbors(selected_v[0])

                _complement_Sk = complement_Sk.copy()
                for n in _complement_Sk:
                    if n[0] in selected_v_neighbors:
                        complement_Sk.remove(n)

                Sk.add(selected_v[0])

            # Si el conjunto encontrado por la hormiga es mejor al que se tenia, actualizar.
            if len(S) < len(Sk):
                S = Sk.copy()
            _G = G.copy()
            # Actualizar la feromona
            update_pheromones(S, node_indexes, pheromone_trail, p, Q)

    return list(S)
