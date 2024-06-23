
from random import randint, shuffle, sample
import rustworkx as rx
from math import inf
import json
import time

from .MIS_heuristic import MIS_heuristic2


def is_MIS(G, S):
    """
    Funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si S es un conjunto independiente maximal

    :param G: grafo dado
    :param S: posible conjunto independiente maximal de G
    :return: true si S es MIS para G, false si no
    """ 
    for i in range(len(S)):
        if S[i] == True and any((S[n] == True) for n in G.neighbors(i)): return False
        if S[i] == False and all((S[n] == False) for n in G.neighbors(i)): return False
    return True


def fitness(G, S):
    """
    Funcion que calcula la aptitud de un genotipo como conjunto independiente

    :param G: Grafo sobre el cual calcular la aptitud
    :param S: genotipo cuya aptitud es calculada
    :return f: aptitud del genotipo como conjunto independiente
    """ 
    f = 0
    for i in range(len(S)):
        if S[i] == True: 
            f += 1 - sum(1 for n in G.neighbors(i) if (S[n] == True)  )
        else:
            f -= all((S[n] == False)  for n in G.neighbors(i) )
    return f

def recomb(G, *P):
    """
    Funcion que recombina un conjunto de genotipos padre

    :param P: lista de padres
    :return: genotipo resultante de la recombinacion
    """ 
    n_nodes =len(G.node_indices())
    nParents = len(P)
    prob = [sum(i) for i in zip(*P)]
    h = []
    S = []
    for i in range(n_nodes):
        valid = False
        if randint(0,nParents) < prob[i]:
            neighbors = G.neighbors(i)
            valid = True
            for n in neighbors:
                if n < len(h) and h[n] == True: 
                    valid = False
                    break
        if valid: S.append(i)
        h.append(valid)
    return S, h

def improve(G, S, h):
    Scopy = [i for i in S]
    shuffle(Scopy)
    for i in Scopy:
        if not h[i]: continue
        for n in G.neighbors(i): h[n] = False

    _G = G.copy()
    for i in S:
        for n in _G.neighbors(i): _G.remove_node(n)
        _G.remove_node(i)
    Sp = MIS_heuristic2(_G)

    for i in Sp: h[i] = True
    return h

def distance(p1, p2):
    return sum(i1 != i2 for (i1,i2) in zip(p1,p2) )
    # paths = {}
    # for i in p1:
    #     shortest_path = [-1, maxL]
    #     for e in p2:
    #         if i == e:
    #             shortest_path = [e, 0]
    #             break
    #         try:
    #             if len(K[i][e]) < shortest_path[1]:
    #                 shortest_path = [e, len(K[i][e])]
    #         except: continue
    #     paths[(i,shortest_path[0])] = shortest_path[1]

    # for e in p2:
    #     shortest_path = [-1, maxL]
    #     for i in p1:
    #         if i == e: 
    #             shortest_path = [i, 0]
    #             break
    #         try:
    #             if len(K[i][e]) < shortest_path[1]:
    #                 shortest_path = [i, len(K[i][e])]
    #         except: continue
    #     paths[(shortest_path[0], e)] = shortest_path[1]

    # return sum(paths.values())

def relink(G, pi, pf):
    indexes = list(range(len(pi)))
    shuffle(indexes)
    relinks = []
    copypi = [i for i in pi]
    for i in indexes:
        if copypi[i] != pf[i]:
            copypi[i] != pf[i]
            rl = [i for i in copypi]
            relinks.append([rl, fitness(G, rl)])
    return relinks

def mutate(S, mutation_rate):
    """
    Funcion que genera una mutacion de un genotipo en base a una tasa de mutacion

    :param S: genotipo a mutar
    :param mutation_rate: tasa de mutacion, cada unidad representa un 0.1 de probabilidad de mutacion
    :return: genotipo resultante de la mutacion
    """ 
    return [i != (randint(0,1000) < mutation_rate) for i in S]


def init_population(G, n_nodes, pop_size, initial_set_size):
    """
    Funcion que genera una poblacion inicial de genotipos de tamaño especificado donde el conjunto 
    que representa cada genotipo tambien tiene un tamaño especificado

    :param n_nodes: numero de nodos del grafo
    :param pop_size: tamaño de la población
    :param initial_set_size: tamaño del conjunto representado por los genotipos generados
    :return pop: poblacion generada
    """ 
    pop = []
    for i in range(pop_size):
        p = [False for e in range(n_nodes)]
        for i in range(initial_set_size):
            p[randint(0,n_nodes-1)] = True
        pop.append([p, fitness(G, p)])
    return pop

def MIS_memetic(G, pop_size, mutation_rate, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo memetico sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param mutation_rate: tasa de mutacion en milesimas de porcentaje
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """ 

    pop = init_population(G, len(G.node_indices()), pop_size, len(MIS_heuristic2(G)))

    best = [[],-inf]
    no_improvement = 0
    while True:
        maxF = [[], -inf] 
        for p in pop:
            if p[1] == None: p[1] = fitness(G, p[0])
            if p[1] > maxF[1]: 
                maxF = p

        if maxF[1] > best[1]:
            best = maxF
            no_improvement = 0
        else: 
            no_improvement +=1
            if no_improvement == max_no_improvement:
                break

        pop.sort(key=lambda p: p[1])
        pop = pop[int(len(pop)/2):]

        children = []
        for i in range(pop_size - len(pop)):
            P = [u[0] for u in sample(pop, max(2,int(pop_size/20)))]
            S, child = recomb(G,*P)
            child = mutate(child, mutation_rate)
            improve(G, S, child)
            children.append([child, None])
        pop += children
    return [i for i in range(len(best[0])) if best[0][i] == True]

def MIS_scatter_search(G, ref_set_size, mutation_rate, relinking_rate, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de busqueda dispersa que implementa
    re-enlazado de caminos sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param mutation_rate: tasa de mutacion en milesimas de porcentaje
    :param relinking_rate: porcentaje de elementos sobre el cual realizar re-enlace
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """ 

    
    pop = init_population(G, len(G.node_indices()), ref_set_size*10, len(MIS_heuristic2(G)))
    relinking_pop = int(ref_set_size*relinking_rate/100)

    best = [[],-inf]
    no_improvement = 0
    while True:

        pop.sort(key=lambda p: p[1])
        refSet = pop[-ref_set_size//2:]
        maxL = refSet[-1]

        if maxL[1] > best[1]:
            best = maxL
            no_improvement = 0
        else: 
            no_improvement +=1
            if no_improvement == max_no_improvement:
                break

        popcopy = json.loads(json.dumps(pop))
        for i in range(ref_set_size//2 + ref_set_size%2):
            popcopy.sort(key=lambda p: distance( p[0], pop[i][0]))
            refSet.append(popcopy[-1])

        children = []
        for i in range(ref_set_size*10 - ref_set_size-relinking_pop):
            P = [u[0] for u in sample(refSet[:ref_set_size//2], 1)] +  [u[0] for u in sample(refSet[ref_set_size//2:], 1)]
            S, child = recomb(G,*P)
            child = mutate(child, mutation_rate)
            improve(G, S, child)
            children.append([child, fitness(G,child)])
        pop = refSet + children

        relinks = []
        for i in range(relinking_pop):
            P = [u[0] for u in sample(refSet[:ref_set_size//2], 2)]
            rl = relink(G, *P)
            relinks += rl
        relinks.sort(key=lambda p: p[1])
        pop = refSet + children + relinks[-relinking_pop:]   


    return [i for i in range(len(best[0])) if best[0][i] == True]


def randomGraph(n, e):
    """
    Funcion que recibe dos enteros n y e, y retorna un Grafo con n nodos y e lados

    :param n: numero de nodos
    :param e: numero de edges
    :return: grafo random con n nodos y e lados
    """
    G = rx.PyGraph()
    for i in range(n):
        G.add_node(0)
    for i in range(e):
        G.add_edge(randint(0, n-1), randint(0, n-1), None)

    return G
