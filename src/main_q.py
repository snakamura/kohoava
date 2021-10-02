import argparse
import math
import numpy as np
from typing import Callable, List, Optional, Tuple
from environment import MutableEnvironment, Thermal, Wind
from fly import fly, plot
from glider import Control, Glider
from position import Position

def main(args) -> None:
    maxAltitude = 500
    numberOfDirections = 36 * 2
    numberOfAngles = 10 * 2
    numberOfBanks = 10 * 2
    numberOfPitchActions = 10
    numberOfRollActions = 10

    stateDigitizer = StateDigitizer(maxAltitude, numberOfDirections, numberOfAngles, numberOfBanks)
    actionControl = ActionControl(numberOfPitchActions, numberOfRollActions)
    q = Q(stateDigitizer.numberOfStates, actionControl.numberOfActions)

    if args.load is not None:
        q.load(args.load)
    else:
        for episode in range(1000):
            def stepTrain(glider: Glider) -> Tuple[Control, Optional[Callable[[Glider], None]]]:
                state = stateDigitizer.state(glider)
                action = q.action(state, episode)
                control = actionControl.control(action)

                def update(nextGlider: Glider) -> None:
                    nextState = stateDigitizer.state(nextGlider)
                    reward = -5 if nextGlider.isStalled else \
                             -1 if nextGlider.position.z <= 0 else \
                              1 if nextGlider.position.z >= maxAltitude else \
                           -0.1 if nextGlider.position.z < glider.position.z else \
                            0.1 if nextGlider.position.z > glider.position.z else 0
                    q.update(state, action, reward, nextState)

                return control, update

            gliders = testFly(maxAltitude, stepTrain)
            print(f"{episode}: {gliders[-1].position.z}")

    def stepTest(glider: Glider) -> Tuple[Control, Optional[Callable[[Glider], None]]]:
        state = stateDigitizer.state(glider)
        action = q.action(state)
        control = actionControl.control(action)
        return control, None
    gliders = testFly(maxAltitude, stepTest)

    for index, glider in enumerate(gliders):
        print(index, glider)
    plot(gliders)

    if args.save is not None:
        q.save(args.save)

def testFly(maxAltitude: float, step: Callable[[Glider], Tuple[Control, Optional[Callable[[Glider], None]]]]) -> List[Glider]:
    maxNumberOfSteps = 1000

    environment = MutableEnvironment()
#    environment.addWind(Wind(1, 0), 100, 1000)
    environment.addThermal(Thermal(0, 0, 100, 1000, 500, 3))

    glider = Glider(Position(-100, 0, 300), 0, 0, 0)

    return fly(glider, environment, maxNumberOfSteps, maxAltitude, step)

State = int
Action = int
Reward = float

class ActionControl:
    def __init__(self, numberOfPitchActions: int, numberOfRollActions: int):
        self.__numberOfPitchActions = numberOfPitchActions
        self.__numberOfRollActions = numberOfRollActions

    @property
    def numberOfActions(self) -> Action:
        return self.__numberOfPitchActions * self.__numberOfRollActions

    def control(self, action: Action) -> Control:
        pitchAction = action % self.__numberOfPitchActions
        pitch = float(pitchAction) / self.__numberOfPitchActions * 2 - 1

        rollAction = int(action / self.__numberOfPitchActions)
        roll = float(rollAction) / self.__numberOfRollActions * 2 - 1

        return Control(pitch, roll)

class StateDigitizer:
    def __init__(self, maxAltitude: float, numberOfDirections: int, numberOfAngles: int, numberOfBanks: int) -> None:
        self.__numberOfZs = int(maxAltitude)
        self.__numberOfDirections = numberOfDirections
        self.__numberOfAngles = numberOfAngles
        self.__numberOfBanks = numberOfBanks

        self.__zBins = StateDigitizer.__bins(0, maxAltitude, self.__numberOfZs)
        self.__directionBins = StateDigitizer.__bins(0, 2 * math.pi, self.__numberOfDirections)
        self.__angleBins = StateDigitizer.__bins(Glider.minAngle, Glider.maxAngle, self.__numberOfAngles)
        self.__bankBins = StateDigitizer.__bins(Glider.minBank, Glider.maxBank, self.__numberOfBanks)

    @property
    def numberOfStates(self) -> State:
        return self.__numberOfZs * self.__numberOfDirections * self.__numberOfAngles * self.__numberOfBanks

    def state(self, glider: Glider) -> State:
        z = np.digitize(glider.position.z, bins=self.__zBins)
        direction = np.digitize(glider.direction, bins=self.__directionBins)
        angle = np.digitize(glider.angle, bins=self.__angleBins)
        bank = np.digitize(glider.bank, bins=self.__bankBins)

        return z + \
            direction * self.__numberOfZs + \
            angle * self.__numberOfZs * self.__numberOfDirections + \
            bank * self.__numberOfZs * self.__numberOfDirections * self.__numberOfAngles

    @staticmethod
    def __bins(min: float, max: float, number: int):
        return np.linspace(min, max, number + 1)[1:-1]

class Q:
    def __init__(self, numberOfStates: State, numberOfActions: Action, eta: float = 0.5, gamma: float = 0.99) -> None:
        self.__numberOfActions = numberOfActions
        self.__eta = eta
        self.__gamma = gamma
        self.__table = np.random.uniform(low=0, high=1, size=(numberOfStates, numberOfActions))

    def action(self, state: State, episode: Optional[int] = None) -> Action:
        isRandom = False
        if episode is not None:
            epsilon = 0.5 * (1 / (episode + 1))
            isRandom = epsilon >= np.random.uniform(0, 1)

        if isRandom:
            return np.random.choice(self.__numberOfActions)
        else:
            return Action(np.argmax(self.__table[state][:]))

    def update(self, state: State, action: Action, reward: Reward, nextState: State) -> None:
        maxQNext = max(self.__table[nextState][:])
        self.__table[state, action] = (self.__table[state, action] +
            self.__eta * (reward + self.__gamma * maxQNext - self.__table[state, action]))

    def save(self, path: str) -> None:
        np.save(path, self.__table)

    def load(self, path: str) -> None:
        self.__table = np.load(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--load")
    parser.add_argument("--save")
    args = parser.parse_args()
    main(args)
