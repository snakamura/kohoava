import matplotlib.pyplot as plt
import numpy as np
from typing import Callable, List, Optional, Tuple
from environment import Environment, MutableEnvironment, Thermal, Wind
from glider import Control, Glider
from position import Position

def testFly(step: Callable[[Glider], Tuple[Control, Optional[Callable[[Glider], None]]]]) -> None:
    maxNumberOfSteps = 1000

    environment = MutableEnvironment()
    environment.addWind(Wind(1, 0), 100, 1000)
    environment.addThermal(Thermal(0, 0, 100, 1000, 100, 3))

    glider = Glider(Position(-100, 0, 300), 0, 0, 0)

    gliders = fly(glider, environment, maxNumberOfSteps, 1000, step)

    for index, glider in enumerate(gliders):
        print(index, glider)
    plot(gliders)

def fly(glider: Glider, environment: Environment, maxNumberOfSteps: int, maxAltitude: float, step: Callable[[Glider], Tuple[Control, Optional[Callable[[Glider], None]]]]) -> List[Glider]:
    gliders: List[Glider] = []

    for n in range(maxNumberOfSteps):
        gliders.append(glider)

        control, next = step(glider)
        glider = glider.apply(control)
        glider = glider.step(environment)
        if next is not None:
            next(glider)

        if glider.position.z <= 0:
            break
        elif glider.position.z >= maxAltitude:
            break

    return gliders

def plot(gliders: List[Glider]) -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    x = np.array(list(map(lambda glider: glider.position.x, gliders)))
    y = np.array(list(map(lambda glider: glider.position.y, gliders)))
    z = np.array(list(map(lambda glider: glider.position.z, gliders)))

    ax.plot(x, y, z, color='blue')
    ax.plot(x, y, color='black')

    plt.show()
