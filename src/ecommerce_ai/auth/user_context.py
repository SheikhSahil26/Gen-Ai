
# Temporary user for development/testing
_DEV_USER_ID = 1


def get_user_id() -> int:
    """
    Return the currently authenticated user ID.

    Temporary implementation:
    Returns a fixed development user ID.

    Later:
    This function will extract and validate the JWT
    and return the user ID from the token.
    """

    return _DEV_USER_ID