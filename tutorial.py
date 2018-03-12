import simple_greedy_agent
from settings import *
from generator import *
from collisions import *
import cnn_agent as agent_interace

"""
GLOBALS
"""

pygame.init()
settings = get_settings()
agent = None

display = pygame.display.set_mode((settings['display_width'], settings['display_height']))
pygame.display.set_caption('Snake')

action_space = [
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})    ,
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}) ,
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})  ,
    pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})  ,
]

default_font = settings['default_font']
title_font = settings['title_font']
score_font = settings['score_font']
SEG_DIM = settings['block_dim']

snake_head_img = None
snake_body_img = None
hor = None
ver = None
apple_img = None
star_img = None
wall_img = None
hole_img = None

head = None
tail = []
tail_rotations = []
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


"""
GAME SETUP
"""

def init_gfx():
    global snake_head_img, snake_body_img, hor, ver, apple_img, star_img, wall_img, hole_img
    snake_head_img = pygame.image.load("snake head.png")
    snake_head_img = pygame.transform.scale(snake_head_img, (SEG_DIM, SEG_DIM))

    snake_body_img = pygame.image.load("snake body.png")
    snake_body_img = pygame.transform.scale(snake_body_img, (SEG_DIM, SEG_DIM))
    hor = snake_body_img
    ver = pygame.transform.rotate(snake_body_img, 90)

    apple_img = pygame.image.load("apple.png")
    apple_img = pygame.transform.scale(apple_img, (SEG_DIM, SEG_DIM))

    star_img = pygame.image.load("star.png")
    star_img = pygame.transform.scale(star_img, (SEG_DIM, SEG_DIM))

    wall_img = pygame.image.load("wall.png")
    wall_img = pygame.transform.scale(wall_img, (SEG_DIM, SEG_DIM))

    hole_img = pygame.image.load("hole.png")
    hole_img = pygame.transform.scale(hole_img, (SEG_DIM, SEG_DIM))


def init_env():
    global facing, direction, opposite, apple
    facing = settings['starting_direction']
    direction = settings['starting_direction']
    opposite = Directions.get_opposite(facing)
    if settings['autostart']:
        direction = facing

    if settings['walls_on']:
        generate_walls(walls, tunnels, settings['display_width'], settings['display_width'], settings['display_height'], settings['wall_max_w'], settings['wall_max_h'])

    if settings['tunnels_on']:
        generate_tunnels(tunnels, walls, settings['tunnel_count'], settings['display_width'], settings['display_height'], SEG_DIM)

    collided = True
    while collided:
        apple = spawn_apple(settings['display_width'], settings['display_height'], SEG_DIM)
        collided = False
        if any_collisions(apple, walls, tunnels, tail, head, [i['star_rect'] for i in stars]):
            collided = True


def init_snake():
    global head, orient_points, tail, tail_rotations
    head = spawn_snake_seg(settings['starting_x'], settings['starting_y'], SEG_DIM, SEG_DIM)
    tail = []
    tail_rotations = []

    for _ in range(settings['starting_tail']):
        move_head(facing)
        tail.append(spawn_snake_seg())


def init_agents():
    global agent
    model = agent_interace.create_model(pygame.surfarray.array3d(display), action_space)
    agent = agent_interace.Agent(model, action_space)


def reset_scores():
    global score, apples_ate, tunnels_burrowed, stars_collected
    score = 0
    apples_ate = 0
    tunnels_burrowed = 0
    stars_collected = 0

def create_game():
    init_gfx()
    init_env()
    init_snake()
    init_agents()


"""
GAME MECHANICS
"""

def move_head(direction):
    global head, tail, head_x, head_y, facing, opposite, snake_head_img

    if direction == opposite:
        direction = facing

    if facing != direction:
        orientate_head(direction)

    if direction == Directions.UP:
        head.top -= SEG_DIM
        facing = Directions.UP
        opposite = Directions.get_opposite(direction)

    elif direction == Directions.RIGHT:
        head.left += SEG_DIM
        facing = Directions.RIGHT
        opposite = Directions.get_opposite(direction)

    elif direction == Directions.DOWN:
        head.top += SEG_DIM
        facing = Directions.DOWN
        opposite = Directions.get_opposite(direction)

    elif direction == Directions.LEFT:
        head.left -= SEG_DIM
        facing = Directions.LEFT
        opposite = Directions.get_opposite(direction)


def orientate_head(direction):
    global snake_head_img
    rotation = facing.value - direction.value
    snake_head_img = pygame.transform.rotate(snake_head_img, rotation)


def move_tail(prev_head, prev_direction):
    global tail, snake_body_img, tail_rotations
    if tail:
        new_tail = tail[1:]
        new_tail.append(prev_head)
        tail = new_tail

        new_rotations = tail_rotations[1:]
        if prev_direction == Directions.UP or prev_direction == Directions.DOWN:
            new_rot = ver
        else:
            new_rot = hor
        new_rotations.append(new_rot)
        tail_rotations = new_rotations


def grow(prev_head, last_direction):
    global head, tail, snake_body_img, tail_rotations
    new_segment = prev_head.copy()
    tail.append(new_segment)

    if last_direction == Directions.RIGHT or last_direction == Directions.LEFT:
        tail_rotations.append(hor)
    else:
        tail_rotations.append(ver)


def burrow_tunnel(tunnel_ind):
    global head, tunnels_burrowed
    emerging_tunnel = tunnel_ind
    while emerging_tunnel == tunnel_ind:
        emerging_tunnel = random.randrange(len(tunnels))

    tunnels_burrowed += 1
    head = tunnels[emerging_tunnel].copy()


def fade_stars():
    for star in stars:
        star['countdown'] -= 1
        if star['countdown'] == 0:
            stars.remove(star)


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
    display.blit(snake_head_img, head)

    display.blit(apple_img, apple)

    for rotation, seg in enumerate(tail):
        display.blit(tail_rotations[rotation], seg)

    for wall in walls:
        start_x = wall.left
        start_y = wall.top
        end_x = wall.left + wall.width
        end_y = wall.top + wall.height

        for i in range(start_x, end_x, SEG_DIM):
            for j in range(start_y, end_y, SEG_DIM):
                block = pygame.Rect(i, j, SEG_DIM, SEG_DIM)
                display.blit(wall_img, block)

    for tunnel in tunnels:
        display.blit(hole_img, tunnel)

    for star in stars:
        display.blit(star_img, star['star_rect'])


    render_score()
    pygame.display.update()
    update_agent()

def update_agent():
    if settings['agent_hook']:
        agent.learn()

def intro_screen():
    global display
    intro = True

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
    global apple
    game_over = False
    clock = pygame.time.Clock()

    state      = pygame.surfarray.array3d(display)
    action     = None
    reward     = None
    next_state = None

    while not done:
        state = pygame.surfarray.array3d(display)

        if game_over:
            if settings['auto_reset']:
                create_game()
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
                            create_game()
                            game_over = False

                        elif event.key == pygame.K_SPACE:
                            game_over = False
                            done = True

        direction = facing

        if settings['agent_hook']:
            pygame.event.post(agent.act(pygame.surfarray.array3d(display)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    direction = Directions.UP

                elif event.key == pygame.K_RIGHT:
                    direction = Directions.RIGHT

                elif event.key == pygame.K_DOWN:
                    direction = Directions.DOWN

                elif event.key == pygame.K_LEFT:
                    direction = Directions.LEFT

                action = action_space[event.type]

        temp_head = head.copy()
        temp_direction = direction
        move_head(direction)

        if settings['walls_on']:
            if has_wall_collided(head, walls):
                game_over = True
        if has_self_collided(head, tail):
            game_over = True

        if has_apple_collided(head, apple, score, settings['apple_reward'], apples_ate):
            reward = settings['apple_reward']
            grow(temp_head, temp_direction)
            collided = True
            while collided:
                apple = spawn_apple(settings['display_width'], settings['display_height'], SEG_DIM)
                collided = False
                if any_collisions(apple, walls, tunnels, tail, head, [i['star_rect'] for i in stars]):
                    collided = True
        else:
            move_tail(temp_head, temp_direction)
        if settings['stars_on']:
            if has_star_collided(head, stars, score, settings['star_reward'], stars_collected):
                reward = settings['star_reward']

        if settings['tunnels_on']:
            tunnel_ind = has_tunnel_collided(head, tunnels)
            if tunnel_ind >= 0:
                burrow_tunnel(tunnel_ind)

        if head.left < 0 or head.left >= settings['display_width'] or head.top < 0 or head.top >= settings[
            'display_height']:
            if settings['auto_reset']:
                display_message("YOU LOSE... Resetting game", pygame.Color('red'))
                create_game()

            else:
                game_over = True

        collided = True
        while collided:
            star = spawn_star(settings['star_prob'], settings['display_width'], settings['display_height'], SEG_DIM)
            if not star:
                break

            collided = False
            if any_collisions(star, head, tail, apple, walls, tunnels):
                collided = True
            stars.append({'star_rect': star, 'countdown': settings['star_countdown']})

        fade_stars()
        clock.tick(10)
        render()
        next_state = pygame.surfarray.array3d(display)

        if settings['agent_hook']:
            reward = reward if not reward == None else 0
            agent.store_memory(state, action, reward, next_state, game_over)



create_game()
done = intro_screen()
game_loop(done)
pygame.quit()
quit()