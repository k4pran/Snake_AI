import pygame
import math
from directions import Directions
from agent import Agent

action_space = [
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}),
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}),
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}),
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}),
]

directions = [
    Directions.UP,
    Directions.RIGHT,
    Directions.DOWN,
    Directions.LEFT
]

class DrunkSnake(Agent):

    def __init__(self, action_space, state_space):
        super().__init__(action_space, state_space)

    def act(self, state):
        head_pos = state[0]
        apple_pos = state[1]
        step_size = state[2]
        facing = state[3]

        shortest = None
        action = action_space[0]
        for i in range(0, len(action_space)):
            if facing == directions[i]:
                continue
            direction = directions[i]
            opposite = Directions.get_opposite(direction)
            x, y = self.pred_position(head_pos.left, head_pos.top, direction, opposite, step_size)
            distance = math.sqrt((apple_pos.top - y)**2 + (apple_pos.left - x)**2)
            if (shortest == None or distance < shortest):
                shortest = distance
                action = action_space[i]

        return action

    def learn(self):
        pass

    def store_memory(self, state, action, reward, next_state, done):
        pass

    def pred_position(self, x, y, direction, opposite, step_size):

        if direction == opposite:
            return x, y

        if direction == Directions.UP:
            y -= step_size
            return x, y

        elif direction == Directions.RIGHT:
            x += step_size
            return x, y

        elif direction == Directions.DOWN:
            y += step_size
            return x, y

        elif direction == Directions.LEFT:
            x -= step_size
            return x, y