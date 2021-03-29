from django.core.validators import validate_email
from ninja import Router, Schema, errors
from ninja.schema import validator

from domains.accounts.services import authenticate_and_create_token
from domains.accounts.services import change_password as update_password
from domains.accounts.services import register_user, update_profile
from web.api.v1.auth_bearer import AuthBearer

router = Router()


class UserSchema(Schema):
    first_name: str
    last_name: str
    username: str
    email: str


class LoginInput(Schema):
    username: str
    password: str


class TokenResponse(Schema):
    token: str


@router.post("/login", response=TokenResponse)
def login(request, input: LoginInput):
    if token := authenticate_and_create_token(
        username=input.username, password=input.password
    ):
        return token

    raise errors.HttpError(status_code=401, message="Unauthorized")


class RegistrationInput(Schema):
    first_name: str
    last_name: str
    username: str
    password: str
    password_confirmation: str
    email: str

    @validator("email", allow_reuse=True)
    def email_has_correct_format(cls, email):
        try:
            validate_email(email)
            return email
        except Exception:
            raise ValueError("Malformed email")

    @validator("password", allow_reuse=True)
    def password_has_minimum_length(cls, password):
        if len(password) < 6:
            raise ValueError("Password too small")
        return password

    @validator("password_confirmation", allow_reuse=True)
    def passwords_must_match(cls, password_confirmation, values):
        if "password" in values and password_confirmation != values["password"]:
            raise ValueError("Passwords must match")
        return password_confirmation


@router.post("/register", response=UserSchema)
def register(request, input: RegistrationInput):
    if new_user := register_user(**input.dict()):
        return new_user

    return errors.HttpError(status_code=409, message="Username already exists")


class ResetPasswordInput(Schema):
    email: str

    @validator("email", allow_reuse=True)
    def email_has_correct_format(cls, email):
        try:
            validate_email(email)
            return email
        except Exception:
            raise ValueError("Malformed email")


@router.post("/password/reset")
def reset_password(request, input: ResetPasswordInput):
    return f"Password reset instructions were sent to {input.email}"


class PasswordChangeInput(Schema):
    old_password: str
    new_password: str
    new_password_confirmation: str

    @validator("new_password_confirmation", allow_reuse=True)
    def passwords_must_match(cls, new_password_confirmation, values):
        if (
            "new_password" in values
            and new_password_confirmation != values["new_password"]
        ):
            raise ValueError("Passwords must match")
        return new_password_confirmation


@router.get("/password/change", auth=AuthBearer())
def change_password(request, input: PasswordChangeInput):
    return update_password(
        user=request.auth,
        old_password=input.old_password,
        new_password=input.new_password,
    )


@router.get("/me", response=UserSchema, auth=AuthBearer())
def me(request):
    return request.auth


class ProfileUpdate(Schema):
    first_name: str
    last_name: str
    email: str

    @validator("email", allow_reuse=True)
    def email_has_correct_format(cls, email):
        try:
            validate_email(email)
            return email
        except Exception:
            raise ValueError("Malformed email")


@router.get("/update", response={200, str}, auth=AuthBearer())
def update(request, input: ProfileUpdate):
    update_profile(**input.dict())

    return 200, "Profile Updated"
