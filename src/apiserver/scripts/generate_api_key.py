import secrets


def generate_api_key(length=32):
    """
    Generate a unique API key.

    Parameters:
    - length (int): The length of the API key (default is 32 characters).

    Returns:
    - str: The generated API key.
    """

    api_key = secrets.token_hex(length // 2)
    return api_key


if __name__ == '__main__':
    api_key = generate_api_key()
    print("Generated API Key:", api_key)
