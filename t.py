import random

import pygame
from directions import Directions
from settings import *
import time
import simple_greedy_agent


"""
GAME SETUP
"""

pygame.init()
settings = get_settings()

display = pygame.display.set_mode((settings['display_width'], settings['display_height']))
pygame.display.set_caption('Snake')

default_font = settings['default_font']
title_font = settings['title_font']
score_font = settings['score_font']

SEG_DIM = settings['block_dim']

snake_head_img = pygame.image.load("snake head.png")
snake_head_img = pygame.transform.scale(snake_head_img, (settings['block_dim'], settings['block_dim']))

snake_body_img = pygame.image.load("snake body.png")
snake_body_img = pygame.transform.scale(snake_body_img, (settings['block_dim'], settings['block_dim']))

apple_img = pygame.image.load("apple.png")
apple_img = pygame.transform.scale(apple_img, (settings['block_dim'], settings['block_dim']))

star_img = pygame.image.load("star.png")
star_img = pygame.transform.scale(star_img, (settings['block_dim'], settings['block_dim']))

wall_img = pygame.image.load("wall.png")
wall_img = pygame.transform.scale(wall_img, (settings['block_dim'], settings['block_dim']))

head = dict()
tail = []
facing = None
opposite = None
direction = None
apple = None
walls = []
tunnels = []
stars = []
score = 0
apples_ate = 0
tunnels_burrowed = 0
stars_collected = 0

def reset(settings, first_play=False):
    global head, tail, facing, opposite, direction, apple, snake_head_img, snake_body_img

    direction = settings['starting_direction']
    opposite = Directions.get_opposite(facing)
    head['rect'] = get_segment()
    head['facing'] = settings['starting_direction']
    apple = spawn_apple()

    snake_head_img = pygame.image.load("snake head.png")
    snake_head_img = pygame.transform.scale(snake_head_img, (settings['block_dim'], settings['block_dim']))

    snake_body_img = pygame.image.load("snake body.png")
    snake_body_img = pygame.transform.scale(snake_body_img, (settings['block_dim'], settings['block_dim']))

    if settings['autostart']:
        direction = facing

    if first_play:
        if settings['walls_on']:
            generate_walls()

        if settings['tunnels_on']:
            generate_tunnels()

    else:
        tail = []

    for _ in range(settings['starting_tail']):
        move_head(head['facing'])
        tail.append(get_segment())



"""
GAME MECHANICS
"""

def move_head(direction):
    global head, tail, head_x, head_y, facing, opposite, snake_head_img

    if direction == opposite:
        direction = head['facing']

    if facing != direction:
        snake_head_img = orientate_snake(snake_head_img, head, direction.value)

    if direction == Directions.UP:
        head['rect'].top -= SEG_DIM
        head['facing'] = Directions.UP
        opposite = Directions.get_opposite(direction)

    elif direction == Directions.RIGHT:
        head['rect'].left += SEG_DIM
        head['facing'] = Directions.RIGHT
        opposite = Directions.get_opposite(direction)

    elif direction == Directions.DOWN:
        head['rect'].top += SEG_DIM
        head['facing'] = Directions.DOWN
        opposite = Directions.get_opposite(direction)

    elif direction == Directions.LEFT:
        head['rect'].left -= SEG_DIM
        head['facing'] = Directions.LEFT
        opposite = Directions.get_opposite(direction)


def move_tail(prev_head):
    global tail
    if tail:
        new_tail = tail[1: len(tail)]
        new_tail.append(prev_head)
        tail = new_tail


def orientate_snake(img, segment, value):
    rotation = segment['facing'].value - value
    img = pygame.transform.rotate(img, rotation)
    return img

def generate_walls():
    global walls, wall_img
    for _ in range(100):
        if settings['wall_density'] >= random.random():
            loc_x = round(random.randrange(0, settings['display_width']) / settings['block_dim']) * settings['block_dim']
            loc_y = round(random.randrange(0, settings['display_height']) / settings['block_dim']) * settings['block_dim']
            width = round(random.randrange(0, settings['wall_max_w']) / settings['block_dim']) * settings['block_dim']
            height = round(random.randrange(0, settings['wall_max_h']) / settings['block_dim']) * settings['block_dim']

            wall_img = pygame.transform.scale(wall_img, (settings['block_dim'], settings['block_dim']))
            walls.append(pygame.Rect([loc_x, loc_y, width, height]))

def generate_tunnels():
    global tunnels
    for _ in range(settings['tunnel_count']):

        collided = True

        while collided:
            x = round(random.randrange(0, settings['display_width'] - settings['block_dim']) / settings['block_dim']) * settings['block_dim']
            y = round(random.randrange(0, settings['display_height'] - settings['block_dim']) / settings['block_dim']) * settings['block_dim']
            tunnel = pygame.Rect(x, y, settings['block_dim'], settings['block_dim'])

            collided = False
            for wall in walls:
                if tunnel.colliderect(wall):
                    collided = True

        tunnels.append(tunnel)


def burrow_tunnel(tunnel_ind):
    global head, tunnels_burrowed
    emerging_tunnel = tunnel_ind
    while emerging_tunnel == tunnel_ind:
        emerging_tunnel = random.randrange(len(tunnels))

    tunnels_burrowed += 1
    head['rect'] = tunnels[emerging_tunnel].copy()

def has_apple_collided():
    global score, apples_ate
    if apple and head['rect'].colliderect(apple):
        score += settings['apple_reward']
        apples_ate += 1
        spawn_apple()
        return True


def has_wall_collided():
    for wall in walls:
        if head['rect'].colliderect(wall):
            return True
    return False


def has_self_collided():
    for seg in tail:
        if head['rect'].colliderect(seg['rect']):
            return True
    return False


def has_tunnel_collided():
    return head['rect'].collidelist(tunnels)


def has_star_collided():
    global stars, stars_collected, score
    star_ind = head['rect'].collidelist([i['star_rect'] for i in stars])
    if star_ind != -1:
        del stars[star_ind]
        stars_collected += 1
        score += settings['star_reward']
        render_score()


def grow(prev_head):
    global tail, snake_body_img
    new_segment = prev_head.copy()
    rotation = prev_head['facing'].value - direction.value
    snake_body_img = pygame.transform.rotate(snake_body_img, rotation)

    tail.append(new_segment)


def get_segment():
    return pygame.Rect(settings['starting_x'], settings['starting_y'], SEG_DIM, SEG_DIM)


def spawn_apple():
    """
    Randomly generate an apple. The old apple will disappear and appear in a new position.
    Rule 1: It cannot land on a walls or tunnels. Assume a collision and iteratively spawn until no collision is found.
    Rule 2: It is allowed to collide with a snake allowing the snake to gain an easy catch.
    :return: a new randomly generated apple.
    """
    global apple
    collided = True
    while collided:
        x = round(random.randrange(0, settings['display_width'] - settings['block_dim']) / settings['block_dim']) * settings['block_dim']
        y = round(random.randrange(0, settings['display_height'] - settings['block_dim']) / settings['block_dim']) * settings['block_dim']
        apple = pygame.Rect(x, y, settings['block_dim'], settings['block_dim'])
        collided = False
        for wall in walls:
            if apple.colliderect(wall):
                collided = True

    return apple


def spawn_star():
    if settings['stars_on']:
        if settings['star_probability'] > random.random():

            collision = True
            while collision:
                x = round(random.randrange(0, settings['display_width'] - settings['block_dim']) / settings['block_dim']) * settings['block_dim']
                y = round(random.randrange(0, settings['display_height'] - settings['block_dim']) / settings['block_dim']) * settings['block_dim']
                star = pygame.Rect(x, y, settings['block_dim'], settings['block_dim'])
                collision = False
                if star.collidelist(tunnels) != -1 or star.collidelist(walls) != -1 or star.colliderect(apple):
                    collision = True

                stars.append({'star_rect': star, 'countdown': settings['star_fade_steps']})

def fade_stars():
    for star in stars:
        star['countdown'] -= 1
        if star['countdown'] == 0:
            stars.remove(star)


def random_color():
    colors = ['green', 'yellow', 'orange', 'purple', 'pink']
    return colors[random.randrange(len(colors))]


def get_text_object(text, color, large_font=False):
    if large_font:
        text_surf = title_font.render(text, True, color)
    else:
        text_surf = default_font.render(text, True, color)
    return text_surf, text_surf.get_rect()


def display_message(message, color, large_font=False, y_displace=0):
    text_surf, text_rect = get_text_object(message, color, large_font)
    text_rect.center = (settings['display_width'] / 2, settings['display_height'] / 2 + y_displace)
    display.blit(text_surf, text_rect)


def render_score():
    text = score_font.render("Score: " + str(score) +
                        "     Stars collected: " + str(stars_collected) +
                        "     Apples ate: "  + str(apples_ate) +
                        "     Tunnels burrowed: " + str(tunnels_burrowed), True, pygame.Color('green'))
    display.blit(text, [0, 0])

def render():
    global head, tail, display, wall_img, walls, snake_head_img

    display.fill(settings['background_color'])
    display.blit(snake_head_img, head['rect'])

    display.blit(apple_img, apple)

    for segment in tail:
        img = orientate_snake(snake_body_img, segment)
        display.blit(img, segment['rect'])

    for wall in walls:
        start_x = wall.left
        start_y = wall.top
        end_x = wall.left + wall.width
        end_y = wall.top + wall.height

        for i in range(start_x, end_x, settings['block_dim']):
            for j in range(start_y, end_y, settings['block_dim']):
                block = pygame.Rect(i, j, settings['block_dim'], settings['block_dim'])
                display.blit(wall_img, block)

    for tunnel in tunnels:
        display.fill(settings['tunnel_color'], tunnel)

    for star in stars:
        display.blit(star_img, star['star_rect'])

    render_score()
    pygame.display.update()

def intro_screen():
    global display
    intro = True
    done = False

    while intro:
        display.fill(settings['background_color'])
        display_message("Welcome to Snake", pygame.Color('green'), large_font=True, y_displace=-150)
        display_message("- Use the arrow buttons to move", pygame.Color('blue'), y_displace=-60)
        display_message("- Eat the apples to grow!", pygame.Color('blue'), y_displace=-20)
        display_message("- Avoid walls, edges and yourself!", pygame.Color('blue'), y_displace=20)
        display_message("- Collect stars for points", pygame.Color('blue'), y_displace=60)
        display_message("- Burrow tunnels at your own risk!!!", pygame.Color('blue'), y_displace=100)
        display_message(" optional features: walls || tunnels || stars", pygame.Color('purple'), y_displace=170)
        display_message("- press ENTER to continue or SPACE to exit game", pygame.Color(random_color()), y_displace=200)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                return done

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = False
                    return done

                elif event.key == pygame.K_SPACE:
                    done = True
                    return done


"""
GAME LOOP
"""

def game_loop(done=False):
    global direction
    game_over = False
    clock = pygame.time.Clock()

    while not done:

        if game_over:
            while game_over:
                display.fill(settings['background_color'])
                display_message("GAME OVER", pygame.Color('red'), True, -60)
                display_message("Press ENTER to play again or SPACE to quit", pygame.Color('black'), False, 50)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                        game_over = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            reset(settings)
                            game_over = False

                        elif event.key == pygame.K_SPACE:
                            game_over = False
                            done = True

        render()

        if settings['agent_hook']:
            pygame.event.post(simple_greedy_agent.act(
                head['rect'], apple, settings['block_dim'], facing, tail
            ))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                print(event)
                if event.key == pygame.K_UP:
                    direction = Directions.UP

                elif event.key == pygame.K_RIGHT:
                    direction = Directions.RIGHT

                elif event.key == pygame.K_DOWN:
                    direction = Directions.DOWN

                elif event.key == pygame.K_LEFT:
                    direction = Directions.LEFT

        temp_head = dict()
        temp_head['rect'] = head['rect'].copy()
        temp_head['facing'] = head['facing']
        move_head(direction)

        if has_wall_collided() or has_self_collided():
            game_over = True

        if has_apple_collided():
            grow(temp_head)
        else:
            tunnel_ind = has_tunnel_collided()
            has_star_collided()
            if tunnel_ind >= 0:
                burrow_tunnel(tunnel_ind)
            move_tail(temp_head)

        if head['rect'].left < 0 or head['rect'].left >= settings['display_width'] \
                or head['rect'].top < 0 or head['rect'].top >= settings[
            'display_height']:
            if settings['auto_reset']:
                display_message("YOU LOSE... Resetting game", pygame.Color('red'))
                reset(settings)

            else:
                game_over = True

        spawn_star()
        fade_stars()
        clock.tick(10)

reset(settings, first_play=True)
done = intro_screen()
game_loop(done)
pygame.quit()
quit()