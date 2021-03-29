from typing import Dict, Optional

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from domains.accounts.models import AuthToken


def create_auth_token(user: User):
    token, _ = AuthToken.objects.get_or_create(user=user)
    return {
        "user": user,
        "token": token.key,
    }


def delete_auth_token(user: User) -> bool:
    try:
        return bool(AuthToken.objects.get(user=user).delete())
    except AuthToken.DoesNotExist:
        return False


def user_for_token(token: str) -> Optional[User]:
    try:
        token_obj = AuthToken.objects.get(key__iexact=token)
        return token_obj.user
    except AuthToken.DoesNotExist:
        return None
    except AuthToken.MultipleObjectsReturned:
        return None


def register_user(
    username: str, password: str, first_name: str, last_name: str, email: str
) -> Optional[User]:
    try:
        user = User.objects.create(
            username=username, first_name=first_name, last_name=last_name, email=email
        )

        user.set_password(password)
        user.save()

        return user
    except Exception:
        return None


def change_password(user: User, old_password: str, new_password: str) -> bool:
    if user := authenticate(username=user.username, password=old_password):
        user.set_password(new_password)
        user.save()
        return True
    return False


def authenticate_and_create_token(
    username: str, password: str
) -> Optional[Dict[str, str]]:
    if user := authenticate(username=username, password=password):
        return create_auth_token(user)
    return None


def update_profile(user: User, first_name: str, last_name: str, email: str):
    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    user.save()
