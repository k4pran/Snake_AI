import pygame
import random
import math
from directions import Directions
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

def act(head_pos, apple_pos, step_size, facing, tail):
    shortest = None
    action = action_space[0]
    for i in range(0, len(action_space)):
        if Directions.get_opposite(facing) == directions[i]:
            continue
        direction = directions[i]
        opposite = Directions.get_opposite(direction)
        x, y = pred_position(head_pos.left, head_pos.top, direction, opposite, step_size)
        if not will_avoid_oneself(x, y, tail):
            continue

        distance = math.sqrt((apple_pos.top - y)**2 + (apple_pos.left - x)**2)
        if shortest == None or distance < shortest:
            shortest = distance
            action = action_space[i]

    return action

def pred_position(x, y, direction, opposite, step_size):

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


def will_avoid_oneself(x, y, tail):
    for seg in tail:
        if x == seg.left and y == seg.top:
            return False
    return True