from numpy.random import choice
from random import random
from math import exp
import rustworkx as rx

from .MIS_heuristic import MIS_heuristic


def f(G, S, c=2):
    """
    Funcion de evaluacion de una posible solucion. Es su tamano pues es lo que buscamos maximizar.
    
    :pram G: grafo del que se quiere obtener solucio
    :param S: solucion
    :param c: una constante natural positiva por la que se multiplicara el numero de edges en grafo inducido por la solucion. c > 1
    :return: evaluacion numerica (funcion objetivo) de la solucion
    """
    G_induced_S = G.subgraph(list(S))
    return -len(S) + (c * G_induced_S.num_edges())


def exptbl(difference_f, T_cycle):
    """
    Funcion que calcula la probabilidad de aceptar un trial que empeore la solucion.
    
    :pram difference_f: diferencia entre la evaluacion del resultado del trial y la evaluacion del mejor resultado
    :param T_cycle: ciclo de calor actual
    :return: probabilidad de aceptar un trial que empeore la solucion
    """
    return exp(-difference_f / T_cycle)


def MIS_simulated_annealing(G, T0 = 10.0, max_cycles=10, max_trials = 250000, max_changes = 20000):
    """
    Recocido simulado para encontrar el conjunto maximo independiente de un grafo G.

    :param G: grafo G
    :param T0: temperatura inicial
    :param max_cycles: numero maximo de ciclos de temperatura a ejecutar
    :param max_trial: en cada ciclo de temperatura se realizan como máximo max_trials. Un trial consiste en seleccionar un vecino de la solución actual.
    :param max_changes: se produce un cambio si se acepta al vecino. Como máximo se permiten max_changes para una temperatura fija.
    :return: indices del grafo que conforman un conjunto independiente maximo
    """
    # Solucion inicial
    S0 = MIS_heuristic(G)

    # Mejor solucion hasta el momento
    S = set(S0)

    # Solucion actual
    _S = S.copy()

    # Evaluacion de la mejor solucion al momento
    best_f = f(G, S)

    # Temperatura en cada ciclo
    T_cycle = T0

    # Si max_cycles, max_trials, max_changes y T0 son lo suficientemente grandes
    # y 1 - alpha (0 < alpha < 1) es suficientemente pequeño, el algoritmo deberia converger a una solucion optima.
    alpha = 0.99

    # Contador del ciclo de temperatura
    cycles = 0

    node_indexes = list(G.node_indexes())

    while cycles < max_cycles:
        trials, changes = 0, 0
        while trials < max_trials and changes < max_changes:
            # Procedemos con el primer ensayo (trial)
            trials += 1

            # Elegimos un vertice random del grafo
            v = choice(node_indexes)

            # Si el vertice esta en la solucion actual, lo sacamos. Si no, lo incluimos y borramos a sus vecinos.
            if v in _S:
                _S.remove(v)
            else:
                _S.add(v)
                v_neighbors = G.neighbors(v)
                for s in S:
                    if s in v_neighbors:
                        _S.discard(s)
            _f = f(G, _S)

            # Si el resultado del ensayo por funcion de evaluacion es mejor que el que se tenia de
            # la mejor solucion al momento, se actualiza la mejor solucion, su evaluacion y se indica
            # que se hizo un cambio
            if _f < best_f:
                S = _S.copy()
                best_f = _f
                changes += 1
            else:
                # De lo contrario, cuando la funcion de evaluacion del trial no sea mejor, consideramos
                # su diferencia con la mejor evaluacion al momento
                difference_f = _f - best_f

                # Si la diferencia es inferior a 10 * T_cycle se acepta aunque sea peor con una probabilidad de
                # e ^ (-(difference_f) / T_cycle). Esto es asi ya que como e ^ -10 es muy pequeno, se elije que si difference_f > 10 * Tk es rechazado.
                if 0 <= difference_f and difference_f < 10 * T_cycle:
                    # Si la temperatura es alta, el procedimiento acepta vecinos que empeoran el resultado con alta probabilidad. A medida que disminuye la temperatura,
                    # también lo hace la probabilidad de aceptar a un vecino que degrada la solucion
                    if exptbl(difference_f, T_cycle) > random():
                        S = _S.copy()
                        best_f = _f
                        changes += 1
            _S = S.copy()
        # Actualizamos la temperatura (nuestro cooling schedule o proceso de enfriamiento)
        T_cycle = T_cycle * alpha
        if changes < max_changes:
            cycles += 1
    return list(S)
