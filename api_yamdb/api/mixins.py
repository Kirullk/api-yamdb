from .validators import validate_username as val_user


class UsernameMixin:
    def validate_username(self, username):
        return val_user(username)
