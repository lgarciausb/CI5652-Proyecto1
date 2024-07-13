
from random import randint, shuffle, sample, choice, random
import rustworkx as rx
from math import inf
import json
import time

from MIS_heuristic import MIS_heuristic2


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
            f += 1 - sum(1 for n in G.neighbors(i) if (S[n] == True))
        else:
            f -= all((S[n] == False) for n in G.neighbors(i))
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
    return [i != (randint(0, 1000) < mutation_rate) for i in S]


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
            p[randint(0, n_nodes-1)] = True
        pop.append([p, fitness(G, p)])
    return pop


def MIS_material_pouch(G, pop_size, planter_replacement_rate, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de material_pouch search sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param planter_replacement_rate: tasa de reemplazo de las peores macetas por iteracion
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """

    # estimar el tamaño de la solucion usando la heuristica
    estimate = len(MIS_heuristic2(G))

    # inicializacion de la poblacion aleatoria
    planters = init_population(G, pop_size, estimate)
    # cantidad de las peores macetas a reemplazar por iteracion
    n_replace = int(pop_size*planter_replacement_rate)

    best = [[], -inf]
    no_improvement = 0
    while True:
        # generar un nuevo componente material con la funcion de mutacion con tasa de mutacion dependiendo de un vuelo de levy
        material_pouch = mutate(choice(planters)[0], levyFlight(random()))
        material_pouch = [material_pouch, fitness(G, material_pouch)]

        # se escoge una maceta aleatorio y se reemplaza su valor por el componente material si el componente material es mejor
        planter = choice(planters)
        if planter[1] < material_pouch[1]:
            planter[0] = material_pouch[0]
            planter[1] = material_pouch[1]

        planters.sort(key=lambda x: x[1])

        # se reemplazan las peores macetas por macetas aleatorios
        planters = init_population(G, n_replace, estimate) + planters[n_replace:]
        planters.sort(key=lambda x: x[1])

        if planters[-1][1] > best[1]:
            best = planters[-1]
            no_improvement = 0
        else:
            no_improvement += 1
            if no_improvement == max_no_improvement:
                break

    return [i for i in range(len(best[0])) if best[0][i] == True]


def MIS_wizard_search(G, pop_size, GMCR, SAR, SM, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de wizard search sobre un grafo para encontrar un conjunto independiente maximo

    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param GMCR: tasa de consideraicon de memoria de grimorio (Grimoire Memory Considering Rate) 
    :param SAR: tasa de ajuste de hechizo (Spell adjustment rate) 
    :param SM: numero de semillas (seed number) es la cantidad máxima de cambio permitida en el ajuste del hechizo de una variable de diseño
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """

    # estimar el tamaño de la solucion usando la heuristica
    estimate = len(MIS_heuristic2(G))

    # inicializacion de la poblacion aleatoria
    GM = init_population(G, pop_size, estimate)
    GM.sort(key=lambda x: x[1])
    best = [[], -inf]
    no_improvement = 0
    while True:

        if randint(0, 100) < GMCR:
            new_grimoire = [choice(GM)[0][i]
                           for i in range(len(G.node_indices()))]
            if randint(0, 100) < SAR:
                new_grimoire = mutate(new_grimoire, SM)
        else:
            new_grimoire = init_population(G, 1, estimate)[0][0]
        new_grimoire = [new_grimoire, fitness(G, new_grimoire)]

        if GM[0][1] < new_grimoire[1]:
            GM[0] = new_grimoire
            GM.sort(key=lambda x: x[1])

        if GM[-1][1] > best[1]:
            best = GM[-1]
            no_improvement = 0
        else:
            no_improvement += 1
            if no_improvement == max_no_improvement:
                break
    return [i for i in range(len(best[0])) if best[0][i] == True]


def MIS_wizard_search_material_pouch(G, pop_size, planter_replacement_rate, GMCR, SAR, SM, max_no_improvement):
    """
    Funcion que ejecuta un algoritmo de wizard_search en conjunto con la busqueda de materiales adecuados
    
    :param G: grafo sobre el que ejecutar el algoritmo
    :param pop_size: tamaño de la población
    :param planter_replacement_rate: tasa de reemplazo de las peores macetas
    :param GMCR: tasa de consideraicon de memoria de grimorio (Grimoire Memory Considering Rate) 
    :param SAR: tasa de ajuste de hechizo (Spell adjustment rate) 
    :param SM: numero de semillas (seed number) es la cantidad máxima de cambio permitida en el ajuste del hechizo de una variable de diseño
    :param max_no_improvement: maximo numero admisible de iteraciones sin mejora
    :return pop: conjunto independiente maximal encontrado, o conjunto encontrado si 
    se excede el numero admisible de iteraciones sin mejora
    """

    # estimar el tamaño de la solucion usando la heuristica
    estimate = len(MIS_heuristic2(G))

    # inicializacion de la poblacion aleatoria
    planters = init_population(G, pop_size, estimate)
    # cantidad de las peores macetas a reemplazar por iteracion
    n_replace = int(pop_size*planter_replacement_rate)

    best = [[], -inf]
    no_improvement = 0
    while True:
        # generar un nuevo componente material aplicando wizard search
        if randint(0, 100) < GMCR:
            material_pouch = [choice(planters)[0][i]
                      for i in range(len(G.node_indices()))]
            if randint(0, 100) < SAR:
                material_pouch = mutate(material_pouch, SM)
        else:
            material_pouch = init_population(G, 1, estimate)[0][0]
        material_pouch = [material_pouch, fitness(G, material_pouch)]

        # se escoge una maceta aleatoria y se reemplaza su valor por el componente material si el componente material es mejor
        planter = choice(planters)
        if planter[1] < material_pouch[1]:
            planter[0] = material_pouch[0]
            planter[1] = material_pouch[1]

        planters.sort(key=lambda x: x[1])

        # se reemplazan las peores macetas por macetas aleatorias
        planters = init_population(G, n_replace, estimate) + planters[n_replace:]
        planters.sort(key=lambda x: x[1])

        if planters[-1][1] > best[1]:
            best = planters[-1]
            no_improvement = 0
        else:
            no_improvement += 1
            if no_improvement == max_no_improvement:
                break

    return [i for i in range(len(best[0])) if best[0][i] == True]
