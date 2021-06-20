from __future__ import annotations
import math
from environment import Environment
from position import Position

class Glider:
    maxAngle: float = math.pi / 18
    minAngle: float = -math.pi / 4
    stallAngle: float = math.pi / 36

    maxBank: float = math.pi / 3
    minBank: float = -math.pi / 3

    def __init__(self, position: Position, direction: float, angle: float, bank: float) -> None:
        self.__position = position
        self.__direction = direction
        self.__angle = angle
        self.__bank = bank

    def __str__(self) -> str:
        return f'position:({self.position}), direction:{self.direction / math.pi * 180:3.0f}, angle:{self.angle / math.pi * 180:3.0f}, bank:{self.bank / math.pi * 180:3.0f}'

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
        if self.angle > Glider.stallAngle:
            return 0
        elif self.angle > 0:
            return 10 - self.angle / Glider.maxAngle * 3
        else:
            return 10 - self.angle / Glider.minAngle * 20

    # @ bank = 0
    #   -10 @ angle > math.pi/36
    #   -0.75 @ angle = math.pi/36
    #   -1 @ angle = 0
    #   -3.25 @ angle = -math.pi/4
    @property
    def verticalVelocity(self) -> float:
        if self.angle > Glider.stallAngle:
            return -10
        else:
            return (-1 + self.angle / Glider.stallAngle * 0.25) * (1 + math.sin(abs(self.bank)))

    @property
    def angularVelocity(self) -> float:
        return -self.bank / 6

    def apply(self, control: Control) -> Glider:
        angle = min(Glider.maxAngle, max(Glider.minAngle, self.angle + control.pitch * math.pi / 36))
        bank = min(Glider.maxBank, max(Glider.minBank, self.bank + control.roll * math.pi / 36))
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
    def __init__(self, pitch: float, roll: float) -> None:
        self.__pitch = pitch
        self.__roll = roll

    def __str__(self) -> str:
        return f'pitch:{self.pitch:3.2f}, roll:{self.roll:3.2f}'

    # -1 <= pitch <= 1
    # 1 means pushing forward
    # -1 means pulling in
    @property
    def pitch(self) -> float:
        return self.__pitch

    # -1 <= roll <= 1
    # 1 means move to the right
    # -1 means move to the left
    @property
    def roll(self) -> float:
        return self.__roll
