from datetime import datetime
from typing import List
from fastapi import HTTPException

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The new created contact.
    :rtype: Contact
    """
    contact = Contact(first_name = body.first_name, last_name = body.last_name, email = body.email, phone = body.phone, birthday = body.birthday, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the note to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactUpdate
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session)  -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the note to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def query_search(query_field: str, query_value: str, user: User, db: Session):
    """
    Returns a list of contacts by the value of one of the fields 
    ['first_name', 'last_name', 'email'] for the user.

    :param query_field: Field to search contact by.
    :type query_field: str
    :param query_value: Search field value.
    :type query_value: str
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    valid_fields = ['first_name', 'last_name', 'email']
    if query_field not in valid_fields:
        raise HTTPException(status_code=404, detail=f"Invalid query field. Valid fields: {valid_fields}")
    
    contacts = db.query(Contact).filter(getattr(Contact, query_field) == query_value, Contact.user_id == user.id).all()
    return contacts


async def birthdays(user: User, db: Session) -> List[Contact]:
    """
    The function returns a list of contacts whose birthday is in the next week for a specific user.

    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
    result = []
    today = datetime.now()
      
    for contact in contacts:
        b_day = datetime(year=datetime.now().year, month=contact.birthday.month, day=contact.birthday.day)
        if b_day < today:
            b_day = b_day.replace(year=datetime.now().year+1)

        time_to_birthday = abs(b_day - today)

        if time_to_birthday.days < 8:
            result.append(contact)

    return result


