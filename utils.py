import string
import random
def password_setter():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))

print(password_setter())

import time
from datetime import datetime

print(datetime.now().now())