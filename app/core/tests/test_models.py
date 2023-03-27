from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models

User = get_user_model()


def sample_user(email='test@hosseindev.ir', password='testpassword'):
    """Create a sample user."""
    return User.objects.create_user(email=email, password=password)


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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """Test the ingredient string representation"""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test that the recipe string representation is working."""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
