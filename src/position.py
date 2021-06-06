from __future__ import annotations

class Position:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.__x = x
        self.__y = y
        self.__z = z

    def __str__(self) -> str:
        return f'x:{self.__x:8.3f}, y:{self.__y:8.3f}, z:{self.__z:7.3f}'

    @property
    def x(self) -> float:
        return self.__x


    @property
    def y(self) -> float:
        return self.__y


    @property
    def z(self) -> float:
        return self.__z

    def move(self, x: float, y: float, z: float) -> Position:
        return Position(self.__x + x, self.__y + y, self.__z + z)
