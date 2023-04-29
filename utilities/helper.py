import bcrypt
import re
import random
from exception.invalid_parameter import InvalidParameter


def hash_registering_password(passwd):
    return bcrypt.hashpw(passwd, bcrypt.gensalt())


def validate_password(passwd, pw_hash):
    return bcrypt.checkpw(passwd.encode(), pw_hash.encode())


def validate_email(string):
    reg_email = r"[^@]+@[^@]+\.[^@]+"
    if not string:
        raise InvalidParameter("Email cannot be blank")
    if not re.match(reg_email, string):
        raise InvalidParameter("Accepted email address format is: username@domain.domain_type")
    return True


def validate_password_value(string):
    if not string:
        raise InvalidParameter("password cannot be blank")
    elif not 20 >= len(string) >= 8:
        raise InvalidParameter("Accepted password length is between 8 and 20 characters inclusive")

    if string:
        alphabetical_characters = "abcdefghijklmnopqrstuvwxyz"
        special_characters = "!@#$%^&*"
        numeric_characters = "0123456789"

        lower_alpha_count = 0
        upper_alpha_count = 0
        special_character_count = 0
        numeric_character_count = 0

        for char in string:
            if char in alphabetical_characters:
                lower_alpha_count += 1
            elif char in alphabetical_characters.upper():
                upper_alpha_count += 1
            elif char in special_characters:
                special_character_count += 1
            elif char in numeric_characters:
                numeric_character_count += 1
            else:
                raise InvalidParameter(
                    "Password must contain only alphanumeric and special characters only from this set (!@#$%^&*)")
        if lower_alpha_count < 1:
            raise InvalidParameter("Password must have at least 1 lowercase character")
        if upper_alpha_count < 1:
            raise InvalidParameter("Password must have at least 1 uppercase character")
        if special_character_count < 1:
            raise InvalidParameter("Password must have at least 1 special (!@#$%^&*) character")
        if numeric_character_count < 1:
            raise InvalidParameter("Password must have at least 1 numeric character")

    return True


def validate_username(string):
    reg_invalid_character = r"[^a-zA-Z0-9]"

    if not string:
        raise InvalidParameter("Usernames cannot be blank")
    if re.findall(reg_invalid_character, string):
        raise InvalidParameter("Usernames must have only alphanumeric characters")
    elif len(string) > 30:
        raise InvalidParameter("Usernames are limited to 30 alphanumeric characters ")
    elif len(string) < 4:
        raise InvalidParameter("Usernames must have at least 4 alphanumeric characters")

    return True


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


def validate_int(number):
    reg_invalid_character = r"[^0-9]"
    number = str(number)
    if re.findall(reg_invalid_character, number):
        raise InvalidParameter("Expected digits only in a number")
    return True


def validate_flight_direction(direction):
    if direction not in {1, 2, 3, 4}:
        raise InvalidParameter("Expected one of 1, 2, 3, or 4")
    return True


def validate_array_of_ints(defense):
    for num in defense:
        validate_int(num)
    return True


def check_attack_effect(attack, planes):
    result_message = 'Miss'
    for plane in planes:
        if plane.get_cockpit() == attack:
            result_message = 'Kill'
        elif attack in plane.get_body():
            result_message = 'Hit'
    return result_message


def random_automatic_attack(attacks, sky_size):
    attacks_set = set(attacks)
    attack = None
    while len(attacks) == len(attacks_set):
        attack = random.randint(1, sky_size * sky_size)
        attacks_set.add(attack)
    return attack
