import argparse
from collections import namedtuple
import numpy as np
import random
import torch
from torch import nn
from torch import optim
from typing import Callable, List, Optional, Tuple
from environment import MutableEnvironment, Thermal, Wind
from fly import fly, plot
from glider import Control, Glider
from position import Position

def main(args) -> None:
    maxAltitude = 500
    numberOfStates = 4
    numberOfPitchActions = 10
    numberOfRollActions = 10
    batchSize = 32
    transitionsCapacity = 10000

    actionControl = ActionControl(numberOfPitchActions, numberOfRollActions)
    dqn = DQN(numberOfStates, actionControl.numberOfActions, batchSize, transitionsCapacity)

    for episode in range(10000):
        def stepTrain(glider: Glider) -> Tuple[Control, Optional[Callable[[Glider], None]]]:
            state = stateFromGlider(glider)
            action = dqn.action(state, episode)
            control = actionControl.control(action)

            def update(nextGlider: Glider) -> None:
                nextState = stateFromGlider(nextGlider)
                reward = -1 if nextGlider.position.z <= 0 else 1 if nextGlider.position.z >= maxAltitude else 0
                transition = makeTransition(state, action, nextState, reward)
                dqn.update(transition)

            return control, update

        testFly(maxAltitude, stepTrain)

    def stepTest(glider: Glider) -> Tuple[Control, Optional[Callable[[Glider], None]]]:
        state = stateFromGlider(glider)
        action = dqn.action(state)
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

State = Tuple[float, float, float, float]
Action = int
Reward = float

def stateFromGlider(glider: Glider) -> State:
    return (
        glider.position.z,
        glider.direction,
        glider.angle,
        glider.bank,
    )

def stateTensor(state: State) -> torch.FloatTensor:
    return torch.FloatTensor([state])

def makeTransition(state: State, action: Action, nextState: State, reward: Reward):
    return Transition(
        stateTensor(state),
        torch.LongTensor([[action]]),
        stateTensor(nextState),
        torch.FloatTensor([reward])
    )

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

Transition = namedtuple('Transition', ('state', 'action', 'nextState', 'reward'))

class Transitions:
    def __init__(self, capacity: int) -> None:
        self.__capacity = capacity
        self.__transitions: List[Transition] = []
        self.__index = 0

    def push(self, transition: Transition) -> None:
        if len(self.__transitions) < self.__capacity:
            self.__transitions.append(transition)
        else:
            self.__transitions[self.__index] = transition

        self.__index = (self.__index + 1) % self.__capacity

    def sample(self, size: int) -> List[Transition]:
        return random.sample(self.__transitions, size)

    def __len__(self):
        return len(self.__transitions)

class DQN:
    def __init__(self, numberOfState: int, numberOfActions: Action, batchSize: int, transitionsCapacity: int, gamma: float = 0.99):
        self.__numberOfActions = numberOfActions
        self.__batchSize = batchSize
        self.__gamma = gamma
        self.__transitions = Transitions(transitionsCapacity)

        fc1Features = 100
        fc2Features = 500
        self.__model = nn.Sequential()
        self.__model.add_module('fc1', nn.Linear(numberOfState, fc1Features))
        self.__model.add_module('relu1', nn.ReLU())
        self.__model.add_module('fc2', nn.Linear(fc1Features, fc2Features))
        self.__model.add_module('relu2', nn.ReLU())
        self.__model.add_module('fc3', nn.Linear(fc2Features, numberOfActions))

        self.__optimizer = optim.Adam(self.__model.parameters(), lr=0.0001)

    def update(self, transition: Transition) -> None:
        self.__transitions.push(transition)

        if len(self.__transitions) < self.__batchSize:
            return

        transitions = self.__transitions.sample(self.__batchSize)

        batch = Transition(*zip(*transitions))
        stateBatch = torch.cat(batch.state)
        actionBatch = torch.cat(batch.action)
        nextStateBatch = torch.cat(batch.nextState)
        rewardBatch = torch.cat(batch.reward)

        self.__model.eval()
        values = self.__model(stateBatch).gather(1, actionBatch)
        nextValues = self.__model(nextStateBatch).max(1)[0].detach()
        expectedValues = rewardBatch + self.__gamma * nextValues

        self.__model.train()
        loss = nn.functional.smooth_l1_loss(values, expectedValues.unsqueeze(1))
        self.__optimizer.zero_grad()
        loss.backward()
        self.__optimizer.step()

    def action(self, state: State, episode: Optional[int] = None) -> Action:
        isRandom = False
        if episode is not None:
            epsilon = 0.5 * (1 / (episode + 1))
            isRandom = epsilon >= np.random.uniform(0, 1)

        if isRandom:
            return random.randrange(self.__numberOfActions)
        else:
            self.__model.eval()
            with torch.no_grad():
                return self.__model(stateTensor(state)).max(1)[1].item()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--load")
    parser.add_argument("--save")
    args = parser.parse_args()
    main(args)
