import jwt
from django.conf import settings


def decode_data(encrypted_data):
    """
    This is the main function that decode data from jwt to a json object
    """
    public_key = open(settings.PUBLIC_KEY_ROOT).read()
    return jwt.decode(encrypted_data, public_key, algorithms=['RS256'])