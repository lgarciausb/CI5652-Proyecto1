
from random import randint, shuffle, sample, choice, random
import rustworkx as rx
from math import inf
import json
import time

from MIS_heuristic import MIS_heuristic2

def is_MIS(G, S):
    """
    Funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si S es un conjunto independiente maximal

    :param G: grafo dado
    :param S: posible conjunto independiente maximal de G
    :return: true si S es MIS para G, false si no
    """
    for node in S:
        if any((neighbor in S) for neighbor in G.neighbors(node)):
            return False
    for node in G.node_indices():
        if node not in S and not any((neighbor in S) for neighbor in G.neighbors(node)):
            return False
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



def levyFlight(u, a=1.6):
    return 1.0/(1.0-u)**(1.0/a)

def mutate(S, mutation_rate):
    """
    Funcion que genera una mutacion de un genotipo en base a una tasa de mutacion

    :param S: genotipo a mutar
    :param mutation_rate: tasa de mutacion, cada unidad representa un 0.1 de probabilidad de mutacion
    :return: genotipo resultante de la mutacion
    """ 
    return [i != (randint(0,1000) < mutation_rate) for i in S]


def init_population(G, pop_size, initial_set_size):
    """
    Funcion que genera una poblacion inicial de genotipos de tamaño especificado donde el conjunto 
    que representa cada genotipo tambien tiene un tamaño especificado

    :param n_nodes: numero de nodos del grafo
    :param pop_size: tamaño de la población
    :param initial_set_size: tamaño del conjunto representado por los genotipos generados
    :return pop: poblacion generada
    """
    n_nodes = len(G.node_indices())
    pop = []
    for i in range(pop_size):
        p = [False for e in range(n_nodes)]
        for i in range(initial_set_size):
            p[randint(0,n_nodes-1)] = True
        pop.append([p, fitness(G, p)])
    return pop

def MIS_cuckoo(G, pop_size, nest_replacement_rate, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de cuckoo search sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param nest_replacement_rate: tasa de reemplazo de los peores nidos por iteracion
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """

    #estimar el tamaño de la solucion usando la heuristica
    estimate = len(MIS_heuristic2(G)) 

    #inicializacion de la poblacion aleatoria
    nests = init_population(G, pop_size, estimate)
    #cantidad de los peores nidos a reemplazar por iteracion
    n_replace = int(pop_size*nest_replacement_rate)

    best = [[],-inf]
    no_improvement = 0
    while True:
        #generar un nuevo cuco con la funcion de mutacion con tasa de mutacion dependiendo de un vuelo de levy
        cuckoo = mutate(choice(nests)[0], levyFlight(random()))
        cuckoo = [cuckoo, fitness(G, cuckoo)]
        
        #se escoge un nido aleatorio y se reemplaza su valor por el cuco si el cuco es mejor
        nest = choice(nests)
        if nest[1] < cuckoo[1]:
            nest[0] = cuckoo[0]
            nest[1] = cuckoo[1]

        nests.sort(key=lambda x:x[1])

        #se reemplazan los peores nidos por nidos aleatorios
        nests = init_population(G, n_replace, estimate) + nests[n_replace:]
        nests.sort(key=lambda x:x[1])
        
        if nests[-1][1] > best[1]:
            best = nests[-1]
            no_improvement = 0
        else: 
            no_improvement +=1
            if no_improvement == max_no_improvement:
                break


    return [i for i in range(len(best[0])) if best[0][i] == True]

def MIS_harmonic(G, pop_size, HMCR, PAR, BW, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de harmony search sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param HMCR: tasa de consideraicon de memoria de harmonia (Harmony Memory Considering Rate) 
    :param PAR: tasa de ajuste de entonacion (Pitch entonation rate) 
    :param BW: distancia de ancho de banda (distance bandwidth) 
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """


    #estimar el tamaño de la solucion usando la heuristica
    estimate = len(MIS_heuristic2(G)) 

    #inicializacion de la poblacion aleatoria
    HM = init_population(G, pop_size, estimate)
    HM.sort(key=lambda x:x[1])
    best = [[],-inf]
    no_improvement = 0
    while True:
        
        if randint(0, 100) < HMCR: 
            new_harmony = [choice(HM)[0][i] for i in range(len(G.node_indices()))]
            if randint(0,100) < PAR:
                new_harmony = mutate(new_harmony, BW)
        else: new_harmony = init_population(G, 1, estimate)[0][0]
        new_harmony = [new_harmony, fitness(G, new_harmony)]

        if HM[0][1] < new_harmony[1]:
            HM[0] = new_harmony
            HM.sort(key=lambda x:x[1])

        if HM[-1][1] > best[1]:
            best = HM[-1]
            no_improvement = 0
        else: 
            no_improvement +=1
            if no_improvement == max_no_improvement:
                break
    return [i for i in range(len(best[0])) if best[0][i] == True]


def MIS_harmonic_cuckoo(G, pop_size, nest_replacement_rate, HMCR, PAR, BW, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de cuckoo search modificada para 
    sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param nest_replacement_rate: tasa de reemplazo de los peores nidos por 
    :param HMCR: tasa de consideraicon de memoria de harmonia (Harmony Memory Considering Rate) 
    :param PAR: tasa de ajuste de entonacion (Pitch entonation rate) 
    :param BW: distancia de ancho de banda (distance bandwidth) 
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """

    #estimar el tamaño de la solucion usando la heuristica
    estimate = len(MIS_heuristic2(G)) 

    #inicializacion de la poblacion aleatoria
    nests = init_population(G, pop_size, estimate)
    #cantidad de los peores nidos a reemplazar por iteracion
    n_replace = int(pop_size*nest_replacement_rate)

    best = [[],-inf]
    no_improvement = 0
    while True:
        #generar un nuevo cuco aplicando harrmony search
        if randint(0, 100) < HMCR: 
            cuckoo = [choice(nests)[0][i] for i in range(len(G.node_indices()))]
            if randint(0,100) < PAR:
                cuckoo = mutate(cuckoo, BW)
        else: cuckoo = init_population(G, 1, estimate)[0][0]
        cuckoo = [cuckoo, fitness(G, cuckoo)]

        #se escoge un nido aleatorio y se reemplaza su valor por el cuco si el cuco es mejor
        nest = choice(nests)
        if nest[1] < cuckoo[1]:
            nest[0] = cuckoo[0]
            nest[1] = cuckoo[1]

        nests.sort(key=lambda x:x[1])

        #se reemplazan los peores nidos por nidos aleatorios
        nests = init_population(G, n_replace, estimate) + nests[n_replace:]
        nests.sort(key=lambda x:x[1])
        
        if nests[-1][1] > best[1]:
            best = nests[-1]
            no_improvement = 0
        else: 
            no_improvement +=1
            if no_improvement == max_no_improvement:
                break


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
