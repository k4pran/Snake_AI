import pygame
import random

action_space = [
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}),
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}),
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}),
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}),
]

def act():
    return action_space[random.randrange(len(action_space))]