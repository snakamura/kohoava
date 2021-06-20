import math
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from itertools import accumulate
from typing import List
from environment import MutableEnvironment, Thermal, Wind
from glider import Control, Glider
from position import Position

def main() -> None:
    random.seed()

    environment = MutableEnvironment()
    environment.addWind(Wind(1, 0), 100, 1000)
    environment.addThermal(Thermal(0, 0, 100, 1000, 100, 3))

    glider = Glider(Position(-100, 0, 300), 0, 0, 0)

    def next(glider: Glider, n: int) -> Glider:
        glider = glider.apply(Control(random.uniform(-1, 1), random.uniform(-1, 1)))
        glider = glider.step(environment)
        return glider

    gliders: List[Glider] = list(filter(lambda glider: glider.position.z >= 0, accumulate(range(100), next, initial=glider)))
    for index, glider in enumerate(gliders):
        print(index, glider)

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
