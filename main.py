from MIS.functions import test_benchmark, test_defined_graphs
from sys import argv

if __name__ == "__main__":

    try:
        project_part = int(argv[1])
        time = int(argv[2])*60
        if (len(argv) == 4 and bool(argv[3])):
            test_defined_graphs(time, project_part)
        else:
            test_benchmark(time, project_part)
    except IndexError:
        print(f"Usage: {argv[0]} <project_part> <time> <defined_graph: optional>")
    except ValueError as e:
        print(f"Error: <time> must be a numeric value")
