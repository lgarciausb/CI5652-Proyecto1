import rustworkx as rx

from numpy.random import choice
from .MIS_ACO import update_pheromones

def heuristic(G, v):
    neighbors = set(G.neighbors(v))

    neighbors_of_neighbors = set()
    for u in neighbors:
        neighbors_of_neighbors = neighbors_of_neighbors.union(
            set(G.neighbors(u)))

    sum_degree_neighbors_of_neighbors = sum(
        [G.degree(u) for u in neighbors_of_neighbors])
    sum_degree_squares_neighbors_of_neighbors = sum(
        [pow(G.degree(u), 2) for u in neighbors_of_neighbors])

    return (len(neighbors_of_neighbors) + 1) * (sum_degree_squares_neighbors_of_neighbors + 1) / ((1/2 * sum_degree_neighbors_of_neighbors) + 1)

def probability(complement_Sk, v_heuristic, pheromone_trail, alpha, beta):
    sum_trail_heuristic = sum([pow(pheromone_trail[u[0]], alpha) * pow(u[1], beta) for u in complement_Sk])
    return pow(pheromone_trail[v_heuristic[0]], alpha) * pow(v_heuristic[1], beta) / sum_trail_heuristic

def update_pheromones(S, node_indexes, pheromone_trail, p, Q):
    for node in node_indexes:
        pheromone_trail[node] = (1 - p) * pheromone_trail[node] 
        
        if node in S:
             pheromone_trail[node] += Q * len(S)

def MIS_ACO_enhanced(G, max_iter=10, number_of_ants=10, alpha=0.5, beta=0.5, Q=0.05, p=0.8, initial_pheromone=1.0):
    node_indexes = list(G.node_indexes())
    pheromone_trail = [initial_pheromone for _ in range(G.num_nodes())]
    heuristics = [heuristic(G, v) for v in node_indexes]

    S = set()
    _G = G.copy()
    for _ in range(max_iter):
        for k in range(number_of_ants):
            Sk = set()
            v = choice(node_indexes)
            Sk.add(v)

            for n in Sk:
                neighbors = list(_G.neighbors(n))
                _G.remove_node(n)
                _G.remove_nodes_from(neighbors)

            complement_Sk = set()
            _node_indexes = _G.node_indexes()
            for n in _node_indexes:
                complement_Sk.add((n, heuristic(_G, n)))

            while (len(complement_Sk) > 0):
                list_complement_Sk = list(complement_Sk)
                selected_v = list_complement_Sk[choice(len(list_complement_Sk), 1, [probability(
                    complement_Sk, v, pheromone_trail, alpha, beta) for v in complement_Sk])[0]]
                complement_Sk.remove(selected_v)
                
                selected_v_neighbors = _G.neighbors(selected_v[0])
                
                _complement_Sk = complement_Sk.copy()
                for n in _complement_Sk: 
                    if n[0] in selected_v_neighbors:
                        complement_Sk.remove(n)

                Sk.add(selected_v[0])

            if len(S) < len(Sk):
                S = Sk.copy()
            _G = G.copy()
        update_pheromones(S, node_indexes, pheromone_trail, p, Q)

    return S
