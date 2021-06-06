import math
from glider import Control
from glider import Glider
from position import Position

def main() -> None:
    glider = Glider(Position(0, 0, 100), 0, 0, 0)
    print(glider)
    for n in range(20):
        glider = glider.apply(Control(0.1, 0.1))
        glider = glider.step()
        print(glider)

if __name__ == '__main__':
    main()
