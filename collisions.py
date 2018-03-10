def has_apple_collided(head, apple, score, reward, apples_ate):
    if apple and head.colliderect(apple):
        score += reward
        apples_ate += 1
        return True
    return False


def has_wall_collided(head, walls):
    return head.collidelist(walls) >= 0


def has_self_collided(head, tail):
    return head.collidelist(tail) >= 0


def has_tunnel_collided(head, tunnels):
    return head.collidelist(tunnels)


def has_star_collided(head, stars, score, reward, stars_collected):
    star_ind = head.collidelist([i['star_rect'] for i in stars])
    if star_ind != -1:
        del stars[star_ind]
        stars_collected += 1
        score += reward
        return True
    return False


def any_collisions(source, *collision_groups):
    if not source:
        return

    for collider in collision_groups:
        if not collider:
            continue
        if isinstance(collider, list):
            if source.collidelist(collider) >= 0:
                return True
        else:
            if source.colliderect(collider):
                return True
    return False