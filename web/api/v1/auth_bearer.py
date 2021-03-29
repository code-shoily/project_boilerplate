from ninja.security import HttpBearer

from domains.accounts.services import user_for_token


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if user := user_for_token(token):
            return user
