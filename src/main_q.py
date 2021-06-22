import math
import numpy as np
from typing import Callable, List, Optional, Tuple
from environment import MutableEnvironment, Thermal, Wind
from fly import fly, plot
from glider import Control, Glider
from position import Position

def main() -> None:
    maxAltitude = 500
    pitchActions = 10
    rollActions = 10

    stateDigitizer = StateDigitizer(maxAltitude)
    q = Q(stateDigitizer.states, pitchActions * rollActions)
    actionControl = ActionControl(pitchActions, rollActions)

    for episode in range(10000):
        def stepTrain(glider: Glider) -> Tuple[Control, Optional[Callable[[Glider], None]]]:
            state = stateDigitizer.state(glider)
            action = q.action(state, episode)
            control = actionControl.control(action)

            def update(nextGlider: Glider) -> None:
                nextState = stateDigitizer.state(nextGlider)
                reward = -1 if nextGlider.position.z <= 0 else 1 if nextGlider.position.z >= maxAltitude else 0.5 if nextGlider.position.z > glider.position.z else 0
                q.update(state, action, reward, nextState)

            return control, update

        testFly(maxAltitude, stepTrain)

    def stepTest(glider: Glider) -> Tuple[Control, Optional[Callable[[Glider], None]]]:
        state = stateDigitizer.state(glider)
        action = q.action(state)
        control = actionControl.control(action)
        return control, None
    gliders = testFly(maxAltitude, stepTest)

    for index, glider in enumerate(gliders):
        print(index, glider)
    plot(gliders)

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
    def __init__(self, pitchActions: int, rollActions: int):
        self.__pitchActions = pitchActions
        self.__rollActions = rollActions

    def control(self, action: Action) -> Control:
        pitchAction = action % self.__pitchActions
        pitch = float(pitchAction) / self.__pitchActions * 2 - 1

        rollAction = int(action / self.__pitchActions)
        roll = float(rollAction) / self.__rollActions * 2 - 1

        return Control(pitch, roll)

class StateDigitizer:
    def __init__(self, maxAltitude: float) -> None:
        self.numberOfZ = int(maxAltitude / 2)
        self.numberOfDirection = 36 * 2
        self.numberOfAngle = 10 * 2
        self.numberOfBank = 10 * 2

        self.__zBins = StateDigitizer.__bins(0, maxAltitude, self.numberOfZ)
        self.__directionBins = StateDigitizer.__bins(0, 2 * math.pi, self.numberOfDirection)
        self.__angleBins = StateDigitizer.__bins(Glider.minAngle, Glider.maxAngle, self.numberOfAngle)
        self.__bankBins = StateDigitizer.__bins(Glider.minBank, Glider.maxBank, self.numberOfBank)

    @property
    def states(self) -> State:
        return self.numberOfZ * self.numberOfDirection * self.numberOfAngle * self.numberOfBank

    def state(self, glider: Glider) -> State:
        z = np.digitize(glider.position.z, bins=self.__zBins)
        direction = np.digitize(glider.direction, bins=self.__directionBins)
        angle = np.digitize(glider.angle, bins=self.__angleBins)
        bank = np.digitize(glider.bank, bins=self.__bankBins)

        return z + \
            direction * self.numberOfZ + \
            angle * self.numberOfZ * self.numberOfDirection + \
            bank * self.numberOfZ * self.numberOfDirection * self.numberOfAngle

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
        if episode is None:
            return Action(np.argmax(self.__table[state][:]))
        else:
            epsilon = 0.5 * (1 / (episode + 1))
            if epsilon < np.random.uniform(0, 1):
                return Action(np.argmax(self.__table[state][:]))
            else:
                return np.random.choice(self.__numberOfActions)

    def update(self, state: State, action: Action, reward: Reward, nextState: State) -> None:
        maxQNext = max(self.__table[nextState][:])
        self.__table[state, action] = (self.__table[state, action] +
            self.__eta * (reward + self.__gamma * maxQNext - self.__table[state, action]))

if __name__ == '__main__':
    main()
