from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Dict


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
