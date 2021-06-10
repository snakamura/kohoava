from __future__ import annotations
import math
from environment import Environment
from position import Position

class Glider:
    __maxAngle: float = math.pi / 18
    __minAngle: float = -math.pi / 4
    __stallAngle: float = math.pi / 36

    __maxBank: float = math.pi / 3
    __minBank: float = -math.pi / 3

    def __init__(self, position: Position, direction: float, angle: float, bank: float) -> None:
        self.__position = position
        self.__direction = direction
        self.__angle = angle
        self.__bank = bank

    def __str__(self) -> str:
        return f'p:({self.position}), d:{self.direction / math.pi * 180:3.0f}, a:{self.angle / math.pi * 180:3.0f}, b:{self.bank / math.pi * 180:3.0f}'

    @property
    def position(self) -> Position:
        return self.__position

    # 0 <= direction < 2pi (counter clockwise)
    # 0 indicates x-direction
    # pi/2 indicates y-direction
    @property
    def direction(self) -> float:
        return self.__direction

    # -math.pi/4 <= angle <= math.pi/18
    # Stall if angle > math.pi/36
    @property
    def angle(self) -> float:
        return self.__angle

    # -pi/3 <= bank <= pi/3
    # bank > 0 means banking to the right
    @property
    def bank(self) -> float:
        return self.__bank

    # @ bank = 0
    #   0 @ angle > math.pi/36
    #   7 @ angle = math.pi/36
    #   10 @ angle = 0
    #   30 @ angle = -math.pi/4
    @property
    def horizontalVelocity(self) -> float:
        if self.angle > Glider.__stallAngle:
            return 0
        elif self.angle > 0:
            return 10 - self.angle / Glider.__maxAngle * 3
        else:
            return 10 - self.angle / Glider.__minAngle * 20

    # @ bank = 0
    #   -10 @ angle > math.pi/36
    #   -0.75 @ angle = math.pi/36
    #   -1 @ angle = 0
    #   -3.25 @ angle = -math.pi/4
    @property
    def verticalVelocity(self) -> float:
        if self.angle > Glider.__stallAngle:
            return -10
        else:
            return (-1 + self.angle / Glider.__stallAngle * 0.25) * (1 + math.sin(abs(self.bank)))

    @property
    def angularVelocity(self) -> float:
        return -self.bank / 3

    def apply(self, control: Control) -> Glider:
        angle = min(Glider.__maxAngle, max(Glider.__minAngle, self.angle + control.pitch))
        bank = min(Glider.__maxBank, max(Glider.__minBank, self.bank + control.horizontal * math.pi / 3))
        return Glider(self.position, self.direction, angle, bank)

    def step(self, environment: Environment) -> Glider:
        position = self.position
        horizontalMove = self.horizontalVelocity
        direction = (self.direction + self.angularVelocity) % (2 * math.pi)
        wind = environment.horizontalWind(position)
        x = math.cos(direction) * horizontalMove + math.cos(wind.direction) * wind.velocity
        y = math.sin(direction) * horizontalMove + math.sin(wind.direction) * wind.velocity
        z = self.verticalVelocity + environment.verticalWindVelocity(position)
        return Glider(self.position.move(x, y, z), direction, self.angle, self.bank)

class Control:
    def __init__(self, pitch: float, horizontal: float) -> None:
        self.__pitch = pitch
        self.__horizontal = horizontal

    # -1 <= pitch <= 1
    # 1 means pushing forward
    # -1 means pulling in
    @property
    def pitch(self) -> float:
        return self.__pitch

    # -1 <= horizontal <= 1
    # 1 means move to the right
    # -1 means move to the left
    @property
    def horizontal(self) -> float:
        return self.__horizontal
