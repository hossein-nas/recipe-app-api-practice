from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creatingg a new user with an email is successful"""
        email = 'test@hosseindev.com'
        password = 'Test@password@123'

        user = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@HOSSEINDEV.com'
        user = User.objects.create_user(email=email, password='123123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new super user"""
        user = User.objects.create_superuser(
            email='test@hosseindev.com',
            password='test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, 'test@hosseindev.com')
