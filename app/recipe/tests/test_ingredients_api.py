from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

User = get_user_model()
INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITest(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """Test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            'test@hosseindev.ir',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients."""

        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = User.objects.create_user(
            'testuser',
            'testpassfortestuser'
        )

        Ingredient.objects.create(
            user=self.user,
            name='Kale',
        )
        Ingredient.objects.create(
            user=user2,
            name='Kale',
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(len(res.data), 1)
