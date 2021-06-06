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

class Environment:
    def __init__(self) -> None:
        pass

    def horizontalWind(self, position: Position) -> Wind:
        return Wind(0, 0)

    def verticalWindVelocity(self, position: Position) -> float:
        return 0
