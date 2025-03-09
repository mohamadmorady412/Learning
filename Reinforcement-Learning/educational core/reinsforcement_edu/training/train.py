from abcs.abcs import AbstractAgent, AbstractEnvironment
from Agents.Agents import QLearningAgent, ValueIterationAgent

# Factory Method
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
