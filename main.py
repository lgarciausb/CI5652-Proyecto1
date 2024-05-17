from MIS.functions import test_benchmark
from sys import argv

if __name__ == "__main__":
   try:
      test_benchmark(int(argv[1])*60)
   except IndexError: print(f"Usage: {argv[0]} <time>")
   except Exception: print(f"Error: <time> must be a numeric value")
