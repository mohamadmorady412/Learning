try:
    import numpy as np
except ImportError:
    np = None
    print("Warning: NumPy is not installed. Some functionalities may not work.")

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class AbstractAgent(ABC):
    states: int
    actions: int
    gamma: float = 0.9
    alpha: float = 0.1
    epsilon: float = 0.1
    
    @abstractmethod
    def choose_action(self, state: int) -> int:
        pass
    
    @abstractmethod
    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        pass

class AbstractEnvironment(ABC):
    @abstractmethod
    def reset(self) -> int:
        pass
    
    @abstractmethod
    def step(self, action: int) -> Tuple[int, float, bool, Dict]:
        pass

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
        done = self.current_state == len(self.states) - 1  #terminal
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
        if np is None:
            raise ImportError("NumPy is required for stochastic environments.")
        next_state = np.random.choice(self.states, p=self.transition_probabilities[self.current_state][action])
        reward = self.reward_matrix[self.current_state][action]
        self.current_state = next_state
        done = self.current_state == len(self.states) - 1
        return next_state, reward, done, {}

class QLearningAgent(AbstractAgent):
    def __post_init__(self):
        if np is None:
            raise ImportError("NumPy is required for Q-learning agent.")
        self.q_table = np.zeros((self.states, self.actions))
    
    def choose_action(self, state: int) -> int:
        if np is None:
            raise ImportError("NumPy is required for Q-learning agent.")
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        return int(np.argmax(self.q_table[state]))
    
    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        best_next_action = int(np.argmax(self.q_table[next_state]))
        self.q_table[state, action] += self.alpha * (reward + self.gamma * self.q_table[next_state, best_next_action] - self.q_table[state, action])

class ValueIterationAgent(AbstractAgent):
    def __post_init__(self):
        if np is None:
            raise ImportError("NumPy is required for Value Iteration agent.")
        self.value_function = np.zeros(self.states)
    
    def value_iteration(self, transition_probabilities: List[List[List[float]]], rewards: List[List[List[float]]], threshold: float = 1e-6) -> None:
        if np is None:
            raise ImportError("NumPy is required for Value Iteration agent.")
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


class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, states: int, actions: int, **kwargs) -> AbstractAgent:
        if agent_type == "Q-learning":
            return QLearningAgent(states, actions, **kwargs)
        elif agent_type == "Value-iteration":
            return ValueIterationAgent(states, actions, **kwargs)
        else:
            raise ValueError("Unsupported agent type")

def train(agent: AbstractAgent, env: AbstractEnvironment, episodes: int = 1000) -> None:
    for episode in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _ = env.step(action)
            agent.update(state, action, reward, next_state)
            state = next_state

@dataclass
class AgentEvaluator:
    agent: AbstractAgent
    env: AbstractEnvironment
    episodes: int = 100
    
    def evaluate(self) -> Dict[str, float]:
        if np is None:
            raise ImportError("NumPy is required for evaluation.")
        total_rewards: List[float] = []
        success_count: int = 0
        steps_per_episode: List[int] = []
        
        for _ in range(self.episodes):
            state = self.env.reset()
            done = False
            total_reward = 0
            steps = 0
            
            while not done:
                action = self.agent.choose_action(state)
                next_state, reward, done, _ = self.env.step(action)
                total_reward += reward
                steps += 1
                state = next_state
            
            total_rewards.append(total_reward)
            steps_per_episode.append(steps)
            if done and state == len(self.env.states) - 1:
                success_count += 1
        
        avg_reward = float(np.mean(total_rewards))
        avg_steps = float(np.mean(steps_per_episode))
        success_rate = float(success_count / self.episodes)
        
        return {
            "Average Reward": avg_reward,
            "Average Steps to Goal": avg_steps,
            "Success Rate": success_rate
        }
