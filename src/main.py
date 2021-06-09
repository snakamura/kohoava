import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from itertools import accumulate
from typing import List
from environment import MutableEnvironment, Thermal, Wind
from glider import Control, Glider
from position import Position

def main() -> None:
    environment = MutableEnvironment()
    environment.addWind(Wind(10, 0), 80, 90)
    environment.addThermal(Thermal(0, 0, 80, 105, 100, 5))

    glider = Glider(Position(0, 0, 100), 0, 0, math.pi / 9)

    def next(glider: Glider, n: int) -> Glider:
        glider = glider.apply(Control(0, 0))
        glider = glider.step(environment)
        return glider

    gliders: List[Glider] = list(accumulate(range(100), next, initial=glider))
    for glider in gliders:
        print(glider)

    plot(gliders)

def plot(gliders: List[Glider]) -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    x = np.array(list(map(lambda glider: glider.position.x, gliders)))
    y = np.array(list(map(lambda glider: glider.position.y, gliders)))
    z = np.array(list(map(lambda glider: glider.position.z, gliders)))

    ax.plot(x, y, z, color='blue')

    plt.show()

if __name__ == '__main__':
    main()
