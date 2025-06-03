from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """User public data with no password"""

    id: int
    username: str
    email: EmailStr
    """ConfigDict is a Pydantic feature that allows you to configure the
    model's behavior. In this case, from_attributes=True means that the model
    will accept attributes from the input data as keyword arguments.
    This is useful for creating models from dictionaries or other objects."""
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublic(TodoSchema):
    id: int
