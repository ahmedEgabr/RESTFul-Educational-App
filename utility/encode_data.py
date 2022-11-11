import jwt
from django.conf import settings


def encode_data(decrypted_data):
    """
    The main function to encode data to a jwt token
    """
    private_key = open(settings.PRIVATE_KEY_ROOT).read()
    return jwt.encode(decrypted_data, private_key, algorithm='RS256')
