current_user = {
    "username": None,
    "role": None,
    "user_id": None,
    "first_name": None,
    "last_name": None
}

def set_current_user(user_data):
    """Set the current user after login."""
    current_user.update(user_data)

def clear_current_user():
    """Clear user session after logout."""
    for key in current_user:
        current_user[key] = None

def get_current_user():
    """Access current user anywhere."""
    return current_user
