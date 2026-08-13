import random
import string

from .constants import CONFIRMATION_CODE_LENGTH


def generate_confirmation_code():
    return ''.join(random.choices(string.digits,
                                  k=CONFIRMATION_CODE_LENGTH))
