import random
import bcrypt


def validate_password(passwd, pw_hash):
    return bcrypt.checkpw(passwd.encode(), pw_hash.encode())


def hash_registering_password(passwd):
    return bcrypt.hashpw(passwd, bcrypt.gensalt())


def build_plane(cockpit, sky_size, flight_direction):
    plane = [cockpit]
    if flight_direction == 'N':
        # Add wings
        for i in range(-2, 3, 1):
            plane.append(cockpit + (i + sky_size))
        # Add body
        plane.append(cockpit + (2 * sky_size))
        # Add tail
        for i in range(-1, 2, 1):
            plane.append(cockpit + (i + (3 * sky_size)))
    if flight_direction == 'W':
        # Add wings
        for i in range(-2, 3, 1):
            plane.append(cockpit + (i * sky_size) + 1)
        # Add body
        plane.append(cockpit + 2)
        # Add tail
        for i in range(-1, 2, 1):
            plane.append(cockpit + (i * sky_size) + 3)
    if flight_direction == 'E':
        # Add wings
        for i in range(-2, 3, 1):
            plane.append(cockpit + (i * sky_size) - 1)
        # Add body
        plane.append(cockpit - 2)
        # Add tail
        for i in range(-1, 2, 1):
            plane.append(cockpit + (i * sky_size) - 3)
    if flight_direction == 'S':
        # Add wings
        for i in range(-2, 3, 1):
            plane.append(cockpit - (i + sky_size))
        # Add body
        plane.append(cockpit - (2 * sky_size))
        # Add tail
        for i in range(-1, 2, 1):
            plane.append(cockpit - (i + (3 * sky_size)))
    plane = tuple(plane)
    return plane


def build_plane_data(plane, sky_size, flight_direction):
    plane_data = [plane, sky_size, flight_direction]
    return tuple(plane_data)


def build_all_planes_for_sky_size(sky_size, plane_length, wings_size):
    planes_data = set()
    for c in range(0, sky_size * sky_size):
        if wings_size - 1 < c % sky_size < sky_size - wings_size and c < sky_size * (sky_size - (plane_length - 1)):
            planes_data.add(build_plane_data(build_plane(c, sky_size, 'N'), sky_size, 1))
        if wings_size - 1 < c % sky_size < sky_size - wings_size and c > sky_size * (plane_length - 1):
            planes_data.add(build_plane_data(build_plane(c, sky_size, 'S'), sky_size, 3))
        if 0 <= c % sky_size < sky_size - (plane_length - 1) and \
                wings_size * sky_size <= c < sky_size * (sky_size - wings_size):
            planes_data.add(build_plane_data(build_plane(c, sky_size, 'W'), sky_size, 4))
        if plane_length - 1 <= c % sky_size < sky_size and \
                wings_size * sky_size + plane_length - 1 <= c < sky_size * (sky_size - wings_size):
            planes_data.add(build_plane_data(build_plane(c, sky_size, 'E'), sky_size, 2))
    return planes_data


def random_automatic_attack(attacks, sky_size):
    attacks_set = set(attacks)
    attack = None
    while len(attacks) == len(attacks_set):
        attack = random.randint(0, sky_size * sky_size - 1)
        attacks_set.add(attack)
    return attack


def evaluate_disconnect(attacks, rnd_attacks, check_opponents_overall_progress):
    attacks_str = ''.join(str(e) for e in attacks)
    rnd_attacks_str = ''.join(str(e) for e in rnd_attacks)
    if check_opponents_overall_progress or len(rnd_attacks) < 4:
        return False
    elif rnd_attacks_str in attacks_str and len(rnd_attacks) >= 4:
        return True


def check_progress(attacks, planes, rnd_attacks):
    healthy_planes = [[p.get_cockpit(), p.get_body()[0]] for p in planes]
    register_kill = False
    for p in healthy_planes:
        if len(p) > 1:
            for a in attacks:
                if p[0] == a and len(p) > 1:
                    p.remove(p[0])
                    if a not in rnd_attacks:
                        register_kill = True
                elif len(p) > 1 and a in p[1]:
                    p[1].remove(a)
                    if not len(p[1]):
                        p.remove(p[1])
                        if a not in rnd_attacks:
                            register_kill = True
    return register_kill


def evaluate_attack(attacks, planes):
    messages = []
    if not attacks:
        return messages
    planes_health_list = []
    for p in planes:
        plane_health = [p.get_cockpit()]
        for i in p.get_body()[0]:
            plane_health.append(i)
        planes_health_list.append(plane_health)
    remaining_defense = list(planes_health_list)
    not_in_defense = True
    for a in attacks:
        for p in planes_health_list:
            if p[0] == a:
                not_in_defense = False
                messages.append([a, "Kill"])
            elif a in p and not p[0] == a:
                not_in_defense = False
                messages.append([a, "Hit"])
        if not_in_defense:
            messages.append([a, "Miss"])
        not_in_defense = True
    for a in attacks:
        for p in remaining_defense:
            if p[0] == a:
                remaining_defense.remove(p)
            elif a in p and len(p) > 2:
                p.remove(a)
            elif a in p and len(p) == 2:
                remaining_defense.remove(p)
                for m in messages:
                    if m[0] == a and m[1] == "Hit":
                        m[1] = "Kill"
    if not len(remaining_defense):
        messages.append("Battle won by last attack!")
    print(messages, attacks)
    return messages


def validate_defense(plane, planes):
    if len(planes) == 0:
        return True
    cockpit = plane.get_cockpit()
    body = plane.get_body()
    for p in planes:
        if cockpit == p.get_cockpit() or cockpit in p.get_body()[0] or \
                p.get_cockpit() in body[0] or bool(set(body[0]) & set(p.get_body()[0])):
            return False
    else:
        return True


