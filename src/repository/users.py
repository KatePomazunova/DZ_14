from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from libgravatar import Gravatar


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieves user specified by email.

    :param email: Email to search user by.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: User, or None if it does not exist.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create new user.

    :param body: The data for the new user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: A user object.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the refresh token for a user.

    :param user: Get the user to update.
    :type user: User
    :param refresh_token: User's refresh token.
    :type refresh_token: str
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Marks the user by email as confirmed in database.

    :param email: Get the email for confirmation.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Email of user.
    :type email: str
    :param url: URL of picture.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: user
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user