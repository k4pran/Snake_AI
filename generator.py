import pygame
from randomize import *

def spawn_snake_seg(x, y, width, height):
    return pygame.Rect(x, y, width, height)


def spawn_apple(width, height, dimension):
    """
    Randomly generate an apple. The old apple will disappear and appear in a new position.
    Rule 1: It cannot land on a walls or tunnels. Assume a collision and iteratively spawn until no collision is found.
    Rule 2: It is allowed to collide with a snake allowing the snake to gain an easy catch.
    :return: a new randomly generated apple.
    """
    x = randomize_value(width - dimension, dimension)
    y = randomize_value(height - dimension, dimension)
    apple = pygame.Rect(x, y, dimension, dimension)
    return apple


def spawn_star(prob, width, height, dimension):
    if prob > random.random():
        x = randomize_value(width - dimension, dimension)
        y = randomize_value(height - dimension, dimension)
        return pygame.Rect(x, y, dimension, dimension)
    else:
        return False


def generate_walls(walls, wall_img, wall_density, display_w, display_h, wall_max_w, wall_max_h, dimensions):
    for _ in range(100):
        if wall_density >= random.random():
            loc_x  = randomize_value(display_w, dimensions)
            loc_y  = randomize_value(display_h, dimensions)
            width  = randomize_value(wall_max_w, dimensions)
            height = randomize_value(wall_max_h, dimensions)

            wall_img = pygame.transform.scale(wall_img, (dimensions, dimensions))
            walls.append(pygame.Rect([loc_x, loc_y, width, height]))


def generate_tunnels(tunnels, walls, tunnels_count, width, height, dimension):
    for _ in range(tunnels_count):
        collided = True
        while collided:
            x = randomize_value(width - dimension, dimension)
            y = randomize_value(height - dimension, dimension)
            tunnel = pygame.Rect(x, y, dimension, dimension)

            collided = False
            if tunnel.collidelist(walls) >= 0:
                collided = True

        tunnels.append(tunnel)


