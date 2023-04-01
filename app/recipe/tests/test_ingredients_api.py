from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
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
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {
            'name': 'Salt',
        }

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(Ingredient.objects.count(), 1)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_ingredient_item(self):
        """Test that can update ingredient name."""
        ingredient = Ingredient.objects.create(name='Salt', user=self.user)

        self.client.patch(
            reverse('recipe:ingredient-detail', args=[ingredient.pk]),
            {
                'name': 'Salty'
            }
        )

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, 'Salty')

    def test_cannot_update_other_users_ingredients(self):
        """Test that cannot update other user's ingredients"""
        new_user = User.objects.create_user('test@newuser.ir', 'testpass')

        ingredient = Ingredient.objects.create(
            name='Salt',
            user=new_user,
        )

        res = self.client.patch(
            reverse('recipe:ingredient-detail', args=[ingredient.pk]),
            {'name': 'Salty'}
        )

        ingredient.refresh_from_db()
        self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ingredient.name, 'Salt')

    def ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assgined to recipes"""
        ingredient_1 = Ingredient.objects.create(user=self.user, name='Apples')
        ingredient_2 = Ingredient.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            user=self.user,
            title='Apple crumble',
            time_minutes=10,
            price=5.00,
        )

        recipe.ingredients.add(ingredient_1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertIn(IngredientSerializer(ingredient_1).data, res.data)
        self.assertNotIn(IngredientSerializer(ingredient_2).data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items."""
        ingredient_1 = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe_1 = Recipe.objects.create(
            user=self.user,
            title='Egges benedict',
            time_minutes=10,
            price=5.00,
        )
        recipe_1.ingredients.add(ingredient_1)
        recipe_2 = Recipe.objects.create(
            user=self.user,
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
        )
        recipe_2.ingredients.add(ingredient_1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
