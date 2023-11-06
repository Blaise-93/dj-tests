import string
import random
def password_setter():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))


def files(file):
    with open(file, "r") as f:
        data = f.read()
        return data
    