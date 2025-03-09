import numpy as np
from dataclasses import dataclass
from abcs.abcs import AbstractAgent, AbstractEnvironment
from typing import List, Dict


@dataclass
class AgentEvaluator:
    agent: AbstractAgent
    env: AbstractEnvironment
    episodes: int = 100
    
    def evaluate(self) -> Dict[str, float]:
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
