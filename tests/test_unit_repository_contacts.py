import unittest
from datetime import datetime, date
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    query_search,
    birthdays,
)


class TestContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(first_name="Kate", last_name="Duka", email="test@test.com", phone="0939090900",
                            birthday="2000-06-07")
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(first_name="Kate", last_name="Duka", email="test@test.com", phone="0939090900",
                            birthday="2000-06-07")
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(first_name="Kate", last_name="Duka", email="test@test.com", phone="0939090900",
                            birthday="2000-06-07")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_query_search(self):
        contacts = [
            Contact(first_name='Ivan', last_name="Petrov", email="ivan@example.com", phone="1234567890",
                    birthday=date(1990, 5, 20)),
            Contact(first_name='Olena', last_name="Ivanova", email="olena@example.com", phone="9876543210",
                    birthday=date(1985, 6, 5)),
            Contact(first_name='Andriy', last_name="Petrov", email="andriy@example.com", phone="5555555555",
                    birthday=date(1992, 7, 10)),
            Contact(first_name='Maria', last_name="Ivanova", email="maria@example.com", phone="1111222233",
                    birthday=date(1994, 9, 8)),
            Contact(first_name='Viktor', last_name="Petrov", email="viktor@example.com", phone="9999888877",
                    birthday=date(1988, 6, 5)),
        ]
        self.session.query().filter_by().filter().all.return_value = [contacts[0], contacts[2], contacts[4]]
        result = await query_search(current_user=self.user, field_name='last_name', field_value='Petrov',
                                    db=self.session)
        expected_result = [contacts[0], contacts[2], contacts[4]]
        self.assertEqual(result, expected_result)

        
    async def test_birthdays(self):
        today = datetime.now()
        contacts = [
            Contact(id=1, first_name='Maryna', birthday=today.replace(month=today.month, day=today.day + 1), user_id=self.user.id),
            Contact(id=2, first_name='Karyna', birthday=today.replace(month=today.month, day=today.day + 4), user_id=self.user.id),
            Contact(id=3, first_name='David', birthday=today.replace(month=today.month, day=today.day + 6), user_id=self.user.id),
            Contact(id=4, first_name='Marat', birthday=today.replace(month=today.month, day=today.day + 15), user_id=self.user.id)   
        ]
        self.session.query().filter().all.return_value = contacts
        result = await birthdays(self.user, self.session)

        self.assertEqual(len(result), 3)
        self.assertIn(contacts[0], result)
        self.assertIn(contacts[1], result)
        self.assertIn(contacts[2], result)
        self.assertNotIn(contacts[3], result)


if __name__ == '__main__':
    unittest.main()
