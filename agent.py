from abc import ABC, abstractmethod
import pygame


class Agent(ABC):

    def __init__(self, action_space, state_space):
        self.action_space = action_space
        self.state_space = state_space

    @abstractmethod
    def act(self, state) -> pygame.event.EventType:
        pass

    @abstractmethod
    def learn(self):
        pass

    @abstractmethod
    def store_memory(self, state, action, reward, next_state, done):
        pass
