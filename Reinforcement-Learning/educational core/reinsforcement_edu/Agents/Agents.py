import numpy as np
from typing import List
from abcs.abcs import AbstractAgent


class QLearningAgent(AbstractAgent):
    def __post_init__(self):
        self.q_table = np.zeros((self.states, self.actions))
    
    def choose_action(self, state: int) -> int:
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)  # Explore
        return int(np.argmax(self.q_table[state]))  # Exploit
    
    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        best_next_action = int(np.argmax(self.q_table[next_state]))
        self.q_table[state, action] += self.alpha * (reward + self.gamma * self.q_table[next_state, best_next_action] - self.q_table[state, action])

class ValueIterationAgent(AbstractAgent):
    def __post_init__(self):
        self.value_function = np.zeros(self.states)
    
    def value_iteration(self, transition_probabilities: List[List[List[float]]], rewards: List[List[List[float]]], threshold: float = 1e-6) -> None:
        while True:
            delta = 0
            new_value_function = np.copy(self.value_function)
            for state in range(self.states):
                action_values = []
                for action in range(self.actions):
                    value = sum([transition_probabilities[state][action][next_state] * 
                                 (rewards[state][action][next_state] + self.gamma * self.value_function[next_state])
                                 for next_state in range(self.states)])
                    action_values.append(value)
                new_value_function[state] = max(action_values)
                delta = max(delta, abs(new_value_function[state] - self.value_function[state]))
            self.value_function = new_value_function
            if delta < threshold:
                break
