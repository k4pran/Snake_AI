from directions import Directions
import pygame


def get_settings(**kwargs):

        settings = {
            'display_width': 800,
            'display_height': 600,
            'background_color': pygame.Color('white'),
            'snake_color': pygame.Color('green'),
            'apple_color': pygame.Color('red'),
            'default_font': pygame.font.Font(None, 25),
            'title_font': pygame.font.Font(None, 50),
            'score_font': pygame.font.Font(None, 30),

            'starting_x': 0,
            'starting_y': 0,
            'starting_direction': Directions.RIGHT,
            'autostart': True,

            'block_dim': 20,
            'auto_reset': True,
            'agent_hook': True,
            'starting_tail': 0,
            'fps': 10,

            'apple_density': 0.002,
            'apple_spawn_rate': 0.001,
            'apple_reward': 5,

            'walls_on': False,
            'wall_density': 0.10,
            'wall_max_w': 50,
            'wall_max_h': 50,
            'wall_color': pygame.Color('brown'),

            'tunnels_on': False,
            'tunnel_count': 4,
            'tunnel_color': pygame.Color('black'),

            'stars_on': True,
            'star_reward': 20,
            'star_prob': 0.005,
            'star_fade': True,
            'star_countdown': 70,
            'star_color': pygame.Color("yellow")
        }

        settings.update(kwargs)
        return settings