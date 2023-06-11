# ver = '2022-5-9-1'

import math


def hex_to_signed_int(val):
    uintval = int(val, 16)
    bits = 4 * (len(val) - 2)
    if uintval >= math.pow(2, bits - 1):
        uintval = int(0 - (math.pow(2, bits) - uintval))
    return uintval


# Use the following methods with:
# entry_validation_positive_numbers = root.register(mm.only_positive_numbers)
# entry_validation_numbers = root.register(mm.only_digits)
# entry_validation_numbers_space = root.register(mm.digits_or_space)
# entry_validation_positive_numbers_comma = root.register(mm.digits_or_comma)

def only_positive_numbers_2(char):
    return char.lstrip('-').isdigit()


def only_positive_numbers(char):
    if char.isdigit():
        return True

    elif char == "":
        return True

    else:
        return False


def only_digits(char):
    return char.isdigit()


def digits_or_comma_or_minus(char):
    digit = char.isdigit()
    comma = False
    minus = False

    if char == ',':
        comma = True
    elif char == '-':
        minus = True
    else:
        comma = False

    return digit | comma | minus


def positive_numbers_or_comma(char):
    if char.isdigit():
        return True

    elif char == "":
        return True

    elif char == ",":
        return True

    else:
        return False


def digits_or_space(char):
    digit = char.isdigit()
    space = char.isspace()
    return digit | space


def print_var_name(var):
    # var_name = [name for name in globals() if globals()[name] is var]
    var_name = [i for i, a in locals().items() if a == var][0]
    return var_name


# def namestr(obj, namespace):
#     return [name for name in namespace if namespace[name] is obj]


def namestr(**kwargs):
    for k, v in kwargs.items():
        print("%s = %s" % (k, repr(v)))
