from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


# Temporario para a aula 03
class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    """User public data with no password"""

    id: int
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserPublic]
