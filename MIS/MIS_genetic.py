
from random import randint, choice, sample
import rustworkx as rx
from math import inf

from MIS_heuristic import MIS_heuristic2


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

def add_cross(S1, S2):
    """
    Funcion que cruza dos genotipos agregando rodos los nodos de ambos en el genotipo resultante

    :param S1: padre 1
    :param S2: padre 2
    :return: genotipo resultante del cruce
    """ 
    return [S1[i] or S2[i] for i in range(len(S1))]

def mix_cross(S1, S2):
    """
    Funcion que cruza dos genotipos escogiendo aleatoriamente nodos de cada uno

    :param S1: padre 1
    :param S2: padre 2
    :return: genotipo resultante del cruce
    """ 
    return [choice([S1[i],S2[i]]) for i in range(len(S1))]

def mutate(S, mutation_rate):
    """
    Funcion que genera una mutacion de un genotipo en base a una tasa de mutacion

    :param S: genotipo a mutar
    :param mutation_rate: tasa de mutacion, cada unidad representa un 0.1 de probabilidad de mutacion
    :return: genotipo resultante de la mutacion
    """ 
    return [i != (randint(0,1000) < mutation_rate) for i in S]


def init_population(n_nodes, pop_size, initial_set_size):
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
        pop.append([p, None])
    return pop

def MIS_genetic(G, pop_size, mutation_rate, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo genetico sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param mutation_rate: tasa de mutacion en milesimas de porcentaje
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """ 

    pop = init_population(len(G.node_indices()), pop_size, len(MIS_heuristic2(G)))

    best = [[],-inf]
    no_improvement = 0
    mutation_factor = 10
    I = 0
    while True:
        #I +=1

        maxF = [[], -inf] 
        for p in pop:
            if p[1] == None: p[1] = fitness(G, p[0])
            if p[1] > maxF[1]: 
                maxF = p

        if maxF[1] > best[1]:
            best = maxF
            no_improvement = 0
            if is_MIS(G, best[0]): break 
        else: 
            no_improvement +=1
            if no_improvement == max_no_improvement:
                break

        avg = sum(p[0].count(True) for p in pop)/len(pop)
        avgf = sum(p[1] for p in pop)/len(pop)
        print(I, "len", best[0].count(True), "score", best[1],"avgl", avg, "avgf", avgf, "maxF", maxF[1], "mut", mutation_rate+no_improvement/mutation_factor)
        
        pop.sort(key=lambda p: p[1])
        pop = pop[int(len(pop)/2):]

        children = []
        for i in range(pop_size - len(pop)):
            p1, p2 = sample(pop, 2)
            child = mix_cross(p1[0],p2[0])
            # sample(pop,1)[0][0]
            child = mutate(child, mutation_rate+no_improvement/mutation_factor)
            children.append([child, None])
        pop += children
        avg = sum(p.count(True) for p in pop)/len(pop)
    return best[0]
