import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)

class TestUser(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email_found(self):
        user = User()
        self.session.query(User).filter(User.email == 'test@mail').first.return_value = user
        result = await get_user_by_email(email='test@mail', db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query(User).filter(User.email == 'test@mail').first.return_value = None
        result = await get_user_by_email(email='test@mail', db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username='Maryna',
                         email='maryna@mail',
                         password='1447MmAa')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_avatar(self):
        email = 'test@mail.com'
        url = 'test.url'
        user = User(email=email, avatar='old_avatar')
        self.session.query(User).filter(User.email == email).first.return_value = user
        result = await update_avatar(email=email, url=url, db=self.session)
        self.assertEqual(result.avatar, user.avatar)
        
    async def test_confirmed_email(self):
        email = 'test@mail.com'
        user = User(email=email, confirmed=False)
        self.session.query(User).filter(User.email == email).first.return_value = user
        await confirmed_email(email=email, db=self.session)
        self.assertTrue(user.confirmed)
        

if __name__ == '__main__':
    unittest.main()
