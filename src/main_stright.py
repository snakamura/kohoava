from fly import testFly
from glider import Control

def main() -> None:
    testFly(lambda glider: Control(0, 0))

if __name__ == '__main__':
    main()
