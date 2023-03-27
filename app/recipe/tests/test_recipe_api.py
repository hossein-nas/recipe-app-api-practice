from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

User = get_user_model()
RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **payload):
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }

    defaults.update(**payload)

    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, **payload):
    defaults = {
        'name': 'Sample tag',
    }
    defaults.update(**payload)
    return Tag.objects.create(user=user, **defaults)


def sample_ingredient(user, **payload):
    defaults = {
        'name': 'Sample ingredient',
    }
    defaults.update(**payload)
    return Ingredient.objects.create(user=user, **defaults)


def recipe_detail(id):
    return reverse('recipe:recipe-detail', args=[id])


class PublicRecipeAPITest(TestCase):
    """Test publicly available api endpoints of recipe app"""

    def test_login_reuiqred(self):
        """Test that anonymouse user cannot access recipes list"""
        res = APIClient().get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test private api endpoints of recipe app"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            'user@hosseindev.ir',
            'testpass',
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_detail(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
