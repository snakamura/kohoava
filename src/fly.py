import matplotlib.pyplot as plt
import numpy as np
from itertools import accumulate
from typing import Callable, List, Optional, Tuple
from environment import Environment, MutableEnvironment, Thermal, Wind
from glider import Control, Glider
from position import Position

def testFly(step: Callable[[Glider], Tuple[Control, Optional[Callable[[Glider], None]]]]) -> None:
    environment = MutableEnvironment()
    environment.addWind(Wind(1, 0), 100, 1000)
    environment.addThermal(Thermal(0, 0, 100, 1000, 100, 3))

    glider = Glider(Position(-100, 0, 300), 0, 0, 0)

    gliders = fly(glider, environment, step)

    for index, glider in enumerate(gliders):
        print(index, glider)
    plot(gliders)

def fly(glider: Glider, environment: Environment, step: Callable[[Glider], Tuple[Control, Optional[Callable[[Glider], None]]]]) -> List[Glider]:
    def next(glider: Glider, n: int) -> Glider:
        control, next = step(glider)
        glider = glider.apply(control)
        glider = glider.step(environment)
        if next is not None:
            next(glider)
        return glider

    return list(filter(lambda glider: glider.position.z >= 0,
        accumulate(range(100), next, initial=glider)))

def plot(gliders: List[Glider]) -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    x = np.array(list(map(lambda glider: glider.position.x, gliders)))
    y = np.array(list(map(lambda glider: glider.position.y, gliders)))
    z = np.array(list(map(lambda glider: glider.position.z, gliders)))

    ax.plot(x, y, z, color='blue')

    plt.show()
