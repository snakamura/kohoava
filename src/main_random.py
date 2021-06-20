import random
from fly import testFly
from glider import Control

def main() -> None:
    random.seed()

    testFly(lambda glider: (Control(random.uniform(-1, 1), random.uniform(-1, 1)), None))

if __name__ == '__main__':
    main()
