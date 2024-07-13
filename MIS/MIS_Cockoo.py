import random

def initialize_population(graph, population_size):
    population = []
    for _ in range(population_size):
        solution = [random.choice([0, 1]) for _ in range(len(graph))]
        population.append(solution)
    return population

def evaluate_solution(solution, graph):
    independent_set = []
    for i in range(len(solution)):
        if solution[i] == 1:
            independent_set.append(i)
            for j in range(len(graph)):
                if graph[i][j] == 1:
                    solution[j] = 0
    return len(independent_set)

def cuckoo_algorithm(graph, population_size = 10, generations = 100):
    population = initialize_population(graph, population_size)

    for _ in range(generations):
        best_solution = max(population, key=lambda x: evaluate_solution(x, graph))

        new_solution = [random.choice([0, 1]) for _ in range(len(graph))]
        if evaluate_solution(new_solution, graph) > evaluate_solution(best_solution, graph):
            index_to_replace = random.randint(0, len(population)-1)
            population[index_to_replace] = new_solution

    best_solution = max(population, key=lambda x: evaluate_solution(x, graph))

    return [i for i in range(len(best_solution)) if best_solution[i] == 1]

# Beispielgraph als Adjazenzmatrix
graph = [
    [0, 1, 0, 1, 0, 0, 1, 0], 
[1, 0, 1, 0, 0, 0, 0, 1], 
[0, 1, 0, 1, 1, 0, 0, 0], 
[1, 0, 1, 0, 0, 1, 0, 0], 
[0, 0, 1, 0, 0, 1, 0, 1], 
[0, 0, 0, 1, 1, 0, 1, 0], 
[1, 0, 0, 0, 0, 1, 0, 1], 
[0, 1, 0, 0, 1, 0, 1, 0], 

]

population_size = 10
generations = 100

result = cuckoo_algorithm(graph, population_size, generations)
print("Maximum Independent Set gefunden:", result)

##################################################################

def generate_random_solution(graph):
    solution = []
    for node in graph:
        if random.random() < 0.5:
            solution.append(node)
    return solution

def fitness(solution, graph):
    independent_set = set(solution)
    fitness_value = 0
    for node in independent_set:
        fitness_value += 1
        for neighbor in graph[node]:
            if neighbor in independent_set:
                fitness_value -= 1
                break
    return fitness_value

def harmony_search(graph, max_iter=100, hms=10, hmcr=0.9, par=0.3):
    best_solution = []
    best_fitness = 0

    for _ in range(max_iter):
        harmony_memory = [generate_random_solution(graph) for _ in range(hms)]

        for _ in range(hms):
            new_solution = []
            for i in range(len(graph)):
                if random.random() < hmcr:
                    new_solution.append(harmony_memory[random.randint(0, hms-1)][i])
                else:
                    if random.random() < par:
                        new_solution.append(1)
                    else:
                        new_solution.append(0)

            current_fitness = fitness(new_solution, graph)
            if current_fitness > best_fitness:
                best_solution = new_solution
                best_fitness = current_fitness

    return best_solution

# Example usage
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'C', 'D'],
    'C': ['A', 'B', 'D'],
    'D': ['B', 'C']
}

solution = harmony_search(graph)
print("Best solution:", solution)