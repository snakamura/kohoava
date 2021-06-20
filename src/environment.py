from abc import ABC, abstractmethod
import math
from typing import List, Optional, cast
from position import Position

class Wind:
    def __init__(self, velocity: float, direction: float) -> None:
        self.__velocity = velocity
        self.__direction = direction

    @property
    def velocity(self) -> float:
        return self.__velocity

    @property
    def direction(self) -> float:
        return self.__direction

class Environment(ABC):
    @abstractmethod
    def horizontalWind(self, position: Position) -> Wind:
        pass

    @abstractmethod
    def verticalWindVelocity(self, position: Position) -> float:
        pass

class Thermal:
    def __init__(self, x: float, y: float, minZ: float, maxZ: float, radius: float, velocity: float, flat: bool = False) -> None:
        self.__x = x
        self.__y = y
        self.__minZ = minZ
        self.__maxZ = maxZ
        self.__radius = radius
        self.__velocity = velocity
        self.__flat = flat

    def velocity(self, position: Position) -> Optional[float]:
        if position.z < self.__minZ or self.__maxZ <= position.z:
            return None

        distance = math.sqrt((position.x - self.__x) ** 2 + (position.y - self.__y) ** 2)
        if distance > self.__radius:
            return None
        elif self.__flat:
            return self.__velocity
        else:
            return math.log2(2 - distance / self.__radius) * self.__velocity

class WindWithRange:
    def __init__(self, wind: Wind, minZ: float, maxZ: float) -> None:
        self.__wind: Wind = wind
        self.__minZ: float = minZ
        self.__maxZ: float = maxZ

    @property
    def wind(self) -> Wind:
        return self.__wind

    def contains(self, position: Position) -> bool:
        return self.__minZ <= position.z and position.z < self.__maxZ

class MutableEnvironment(Environment):
    def __init__(self) -> None:
        self.__winds: List[WindWithRange] = []
        self.__thermals: List[Thermal] = []

    def addWind(self, wind: Wind, minZ: float, maxZ: float) -> None:
        self.__winds.append(WindWithRange(wind, minZ, maxZ))

    def addThermal(self, thermal: Thermal) -> None:
        self.__thermals.append(thermal)

    def horizontalWind(self, position: Position) -> Wind:
        wind = next(filter(lambda w: w.contains(position), self.__winds), None)
        if wind is None:
            return Wind(0, 0)
        else:
            return wind.wind

    def verticalWindVelocity(self, position: Position) -> float:
        velocity = next(filter(lambda v: v is not None, map(lambda thermal: thermal.velocity(position), self.__thermals)), None)
        if velocity is None:
            return 0
        else:
            return velocity

Environment.register(MutableEnvironment)
