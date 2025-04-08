from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models import User


def test_create_user(session: Session):
    user = User(
        username='fztrevisan',
        email='fernandineo@mail.com',
        password='123456',
    )

    session.add(user)
    session.commit()
    # refresh the user object to get the updated values from the database
    # (e.g., the auto-generated ID)
    # session.refresh(user)

    result = session.scalar(select(User).where(User.username == 'fztrevisan'))

    assert result.username == 'fztrevisan'
