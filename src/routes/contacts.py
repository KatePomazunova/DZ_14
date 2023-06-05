from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.database.models import User
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix='/contacts', tags=["contacts"])

# Отримати список всіх контактів
@router.get("/contacts/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param current_user: The user to retrieve contacts for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


# Отримати один контакт за ідентифікатором
@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param current_user: The user to retrieve the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID
    :rtype: Contact
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The contact is not found")
    return contact


# Створити новий контакт
@router.post("/create/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param current_user: The user to create the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The new created contact.
    :rtype: Contact
    """
    return await repository_contacts.create_contact(body, current_user, db)


# Оновити існуючий контакт
@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the note to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactUpdate
    :param current_user: The user to update the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact
    :rtype: Contact
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The contact is not found")
    return contact


# Видалити контакт
@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the note to remove.
    :type contact_id: int
    :param current_user: The user to remove the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact.
    :rtype: Contact
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The contact is not found")
    return contact


# Пошук за іменем, прізвищем чи адресою електронної пошти
@router.get("/{query_field}/{query_value}", response_model=List[ContactResponse])
async def query_search(query_field: str = '', query_value: str = '', db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns a list of contacts by the value of one of the fields 
    ['first_name', 'last_name', 'email'] for the user.

    :param query_field: Field to search contact by.
    :type query_field: str
    :param query_value: Search field value.
    :type query_value: str
    :param current_user: The user to retrieve contacts for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = await repository_contacts.query_search(query_field, query_value, current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts are not found")
    return contacts


# Отримати список контактів з днями народження на найближчі 7 днів
@router.get("/birthdays/", response_model=List[ContactResponse])
async def birthdays(db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    The function returns a list of contacts whose birthday is in the next week for a specific user.

    :param current_user: The user to retrieve contacts for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = await repository_contacts.birthdays(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts are not found")
    return contacts