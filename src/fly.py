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
    thermals = [Thermal(0, 0, 100, 600, 500, 3)]
    for thermal in thermals:
        environment.addThermal(thermal)

    glider = Glider(Position(-100, 0, 300), 0, 0, 0)

    gliders = fly(glider, environment, maxNumberOfSteps, 1000, step)

    for index, glider in enumerate(gliders):
        print(index, glider)
    plot(gliders, thermals)

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

def plot(gliders: List[Glider], thermals: List[Thermal] = []) -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    x = np.array(list(map(lambda glider: glider.position.x, gliders)))
    y = np.array(list(map(lambda glider: glider.position.y, gliders)))
    z = np.array(list(map(lambda glider: glider.position.z, gliders)))

    ax.plot(x, y, z, color='blue')
    ax.plot(x, y, color='black')

    for thermal in thermals:
        thermalX, thermalY, thermalZ = cylinder(thermal.x, thermal.y, thermal.minZ, thermal.maxZ, thermal.radius)
        ax.plot_surface(thermalX, thermalY, thermalZ, color='yellow', alpha=0.3)

    plt.show()

def cylinder(x: float, y: float, minZ: float, maxZ: float, radius: float):
    gridZ = np.linspace(minZ, maxZ, 50)
    theta = np.linspace(0, 2 * np.pi, 50)
    gridTheta, gridZ = np.meshgrid(theta, gridZ)
    gridX = radius * np.cos(gridTheta) + x
    gridY = radius * np.sin(gridTheta) + y
    return gridX, gridY, gridZ
