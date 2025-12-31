from django.test import TestCase
from .models import User

class UserTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(email='test@example.com', username='test', password='password')
        self.assertEqual(user.email, 'test@example.com')
