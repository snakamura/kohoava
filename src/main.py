import math
from environment import MutableEnvironment, Wind
from glider import Control, Glider
from position import Position

def main() -> None:
    environment = MutableEnvironment()
    environment.addWind(Wind(10, 0), 80, 90)

    glider = Glider(Position(0, 0, 100), 0, 0, 0)
    print(glider)
    for n in range(20):
        glider = glider.apply(Control(0, 0))
        glider = glider.step(environment)
        print(glider)

if __name__ == '__main__':
    main()
