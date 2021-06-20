from fly import testFly
from glider import Control

def main() -> None:
    testFly(lambda glider: (Control(0, 0), None))

if __name__ == '__main__':
    main()
