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
