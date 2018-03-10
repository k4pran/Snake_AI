import random

def randomize_value(value, SEG_DIM):
    return round(random.randrange(value) / SEG_DIM) * SEG_DIM


def random_color():
    colors = ['green', 'yellow', 'orange', 'purple', 'pink']
    return colors[random.randrange(len(colors))]