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
        attack = random.randint(1, sky_size * sky_size)
        attacks_set.add(attack)
    return attack


def evaluate_disconnect(attacks, rnd_attacks, check_opponents_overall_progress):
    attacks_str = ''.join(str(e) for e in attacks)
    rnd_attacks_str = ''.join(str(e) for e in rnd_attacks)
    if check_opponents_overall_progress:
        return False
    elif rnd_attacks_str in attacks_str and len(rnd_attacks_str) < 4:
        return False
    else:
        return True


def check_progress(attacks, planes, def_size):
    cockpits = []
    bodies_list = []
    counter = 0
    for p in planes:
        cockpits.append(p.get_cockpit())
        bodies_list.append(p.get_body())
    for a in attacks:
        if a in cockpits:
            cockpits.remove(a)
            counter += 1
            for p in planes:
                if a == p.get_cockpit():
                    bodies_list.remove(p.get_body())
        for body in bodies_list:
            if a in body:
                body.remove(a)
    for body in bodies_list:
        if not body:
            counter += 1
    if counter * 100 / def_size > 66.6:
        return True
    else:
        return False


def evaluate_attack(attacks, planes):
    messages = []
    planes_health_list = []
    for p in planes:
        plane_health = [p.get_cockpit()]
        for i in p.get_body():
            plane_health.append(i)
        planes_health_list.append(plane_health)
    print("initial")
    print(planes_health_list)
    for a in attacks:
        for p in planes_health_list:
            if p[0] == a:
                messages.append((a, "Kill"))
                planes_health_list.remove(p)
                break
            elif a in p[1]:
                p[1].remove(a)
                if not p[1]:
                    messages.append((a, "Kill"))
                messages.append((a, "Hit"))
                break
        else:
            messages.append((a, "Miss"))
    print(planes_health_list)
    if not planes_health_list or {len(i[1]) for i in planes_health_list} == 0:
        print(planes_health_list)
        messages.append("Battle won by last attack!")
    return messages


def validate_defense(plane, planes):
    if len(planes) == 0:
        return True
    for p in planes:
        if plane.get_cockpit() == p.get_cockpit() or plane.get_cockpit() in p.get_body():
            return False
        elif p.get_cockpit() in plane.get_body():
            return False
        elif bool(set(plane.get_body()) & set(p.get_body())):
            return False
    else:
        return True


