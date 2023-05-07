import numbers
import re
from exception.invalid_parameter import InvalidParameter


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


def validate_int(number):
    print(number)
    if not str(number).isdigit():
        raise InvalidParameter("Not a positive int")
    else:
        return True


def validate_flight_direction(direction):
    if direction not in {1, 2, 3, 4}:
        raise InvalidParameter("Expected one of 1, 2, 3, or 4")
    return True


def validate_array_of_ints(defense):
    for num in defense:
        validate_int(num)
    return True
