import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

User = get_user_model()
RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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
        recipes = Recipe.objects.all().order_by('-id')
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

    def test_create_basic_recipe(self):
        """Test creating recipe"""

        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }

        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")

        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertEqual(payload['title'], res.data['title'])
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with Ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name="Prawns")
        ingredient2 = sample_ingredient(user=self.user, name="Ginger")

        payload = {
            'title': 'Avocado lime cheesecake',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 60,
            'price': 20.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(payload['title'], res.data['title'])
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_create_recipe_with_wrong_tags_will_result_in_error(self):
        """Test that sending wrong tag id results in error"""
        payload = {
            'title': 'Avocado lime cheesecake',
            'ingredients': [999, 9999],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        exists = Recipe.objects \
            .filter(title='Avocado lime cheesecake').exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(exists)

    def test_partial_update_recipe(self):
        """Test updating a recipe with PATCH"""
        recipe = sample_recipe(user=self.user)
        old_tag = sample_tag(user=self.user, name="OldTag")
        new_tag = sample_tag(user=self.user, name="NewTag")
        recipe.tags.add(old_tag)

        res = self.client.patch(recipe_detail(recipe.id), {
            'title': 'Chicken tikka',
            'tags': [new_tag.id]
        })

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(new_tag, recipe.tags.all())
        self.assertEqual(res.data['title'], 'Chicken tikka')

    def test_full_update_recipe(self):
        """Test full updating a recipe with PUT"""
        recipe = sample_recipe(user=self.user)
        old_tag = sample_tag(user=self.user, name="OldTag")
        new_tag = sample_tag(user=self.user, name="NewTag")
        recipe.tags.add(old_tag)

        res = self.client.put(recipe_detail(recipe.id), {
            'title': 'Chicken tikka',
            'tags': [new_tag.id],
            'time_minutes': 111,
            'price': 111.00
        })

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(new_tag, recipe.tags.all())
        self.assertEqual(getattr(recipe, 'title'), 'Chicken tikka')
        self.assertEqual(getattr(recipe, 'price'), 111.00)
        self.assertEqual(getattr(recipe, 'time_minutes'), 111)


class RecipeImageUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('user@hosseindev.ir',
                                             'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()
        super().tearDown()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)

            res = self.client.post(url, {'image': ntf}, format="multipart")

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_wrong_image_to_recipe(self):
        """Test uploading a wrong image to recipe"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'badimage'}, format="multipart")

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
