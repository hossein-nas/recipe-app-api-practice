from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

User = get_user_model()

TAGS_URL = reverse('recipe:tag-list')


def TAGS_RETRIEVE_URL(id=None):
    return reverse('recipe:tag-detail', kwargs={'pk': id})


class PublicAPITests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = User.objects.create_user(
            'test@hosseindev.ir',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user."""
        user = User.objects.create_user(
            'other@hosseindev.ir',
            'password123'
        )

        Tag.objects.create(user=user, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_invalid_name(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_delete_other_users_tags(self):
        """Test that any user cannot delete other user's tag"""
        new_user = User.objects.create_user('test@testdev.ir', 'test')
        new_user_tag = Tag.objects.create(name='new_user_tag', user=new_user)
        user_tag = Tag.objects.create(name='new_tag', user=self.user)

        self.assertEqual(len(Tag.objects.all()), 2)

        res = self.client.delete(TAGS_RETRIEVE_URL(new_user_tag.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        res = self.client.delete(TAGS_RETRIEVE_URL(user_tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(len(Tag.objects.all()), 1)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assgined to recipes"""
        tag_1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag_2 = Tag.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.objects.create(
            user=self.user,
            title='Coriandier eggs on toast',
            time_minutes=10,
            price=5.00,
        )

        recipe.tags.add(tag_1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertIn(TagSerializer(tag_1).data, res.data)
        self.assertNotIn(TagSerializer(tag_2).data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items."""
        tag_1 = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe_1 = Recipe.objects.create(
            user=self.user,
            title='Pancakes',
            time_minutes=10,
            price=5.00,
        )
        recipe_1.tags.add(tag_1)
        recipe_2 = Recipe.objects.create(
            user=self.user,
            title='Porridge',
            time_minutes=10,
            price=5.00,
        )
        recipe_2.tags.add(tag_1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
