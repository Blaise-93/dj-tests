import string
import random
import uuid


def password_setter():
    """ generate a random password for each user in our database until the client/
    patients/agent changes the password when the person request to change it. While,
    we allow django auth admin to hash the user's password."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))


def slug_modifier():
    """
    Generate a random string code as an adjunct to the patients' slug to
    mask it from the user or any other person viewing the URI. 
    So, we don't want the set slug to be easily identified.
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def files(file):
    """ A helper function to upload and read individual files when sending emails to
    the user. """
    with open(file, "r") as f:
        data = f.read()
        return data


def generate_patient_unique_code():
    """
    Generate a random, unique order number using UUID for our patients
    """
    return uuid.uuid4().hex.upper()

import argparse