from abc import ABC, abstractmethod
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

    def addWind(self, wind: Wind, minZ: float, maxZ: float) -> None:
        self.__winds.append(WindWithRange(wind, minZ, maxZ))

    def horizontalWind(self, position: Position) -> Wind:
        wind = next(filter(lambda w: w.contains(position), self.__winds), None)
        if wind is None:
            return Wind(0, 0)
        else:
            return wind.wind

    def verticalWindVelocity(self, position: Position) -> float:
        return 0

Environment.register(MutableEnvironment)
