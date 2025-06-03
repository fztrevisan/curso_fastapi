from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


class TodoState(StrEnum):
    draft = auto()
    todo = auto()
    doing = auto()
    done = auto()
    trash = auto()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    tite: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
