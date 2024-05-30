from MIS.functions import test_benchmark, test_defined_graphs
from sys import argv

if __name__ == "__main__":

    try:
        time = int(argv[1])*60
        if (len(argv) == 3 and bool(argv[2])):
            test_defined_graphs(time)
        else:
            test_benchmark(time)
    except IndexError:
        print(f"Usage: {argv[0]} <time> <defined_graph: optional>")
    except ValueError as e:
        print(f"Error: <time> must be a numeric value")
