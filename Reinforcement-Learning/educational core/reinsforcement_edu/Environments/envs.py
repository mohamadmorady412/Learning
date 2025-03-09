import numpy as np
from typing import List, Tuple, Dict
from abcs.abcs import AbstractEnvironment


class DeterministicEnvironment(AbstractEnvironment):
    def __init__(self, states: List[int], transition_matrix: List[List[int]], reward_matrix: List[List[float]]):
        self.states = states
        self.transition_matrix = transition_matrix
        self.reward_matrix = reward_matrix
        self.current_state: int = 0
    
    def reset(self) -> int:
        self.current_state = 0
        return self.current_state
    
    def step(self, action: int) -> Tuple[int, float, bool, Dict]:
        next_state = self.transition_matrix[self.current_state][action]
        reward = self.reward_matrix[self.current_state][action]
        self.current_state = next_state
        done = self.current_state == len(self.states) - 1  # Assuming last state is terminal
        return next_state, reward, done, {}

class StochasticEnvironment(AbstractEnvironment):
    def __init__(self, states: List[int], transition_probabilities: List[List[List[float]]], reward_matrix: List[List[float]]):
        self.states = states
        self.transition_probabilities = transition_probabilities
        self.reward_matrix = reward_matrix
        self.current_state: int = 0
    
    def reset(self) -> int:
        self.current_state = 0
        return self.current_state
    
    def step(self, action: int) -> Tuple[int, float, bool, Dict]:
        next_state = np.random.choice(self.states, p=self.transition_probabilities[self.current_state][action])
        reward = self.reward_matrix[self.current_state][action]
        self.current_state = next_state
        done = self.current_state == len(self.states) - 1
        return next_state, reward, done, {}
