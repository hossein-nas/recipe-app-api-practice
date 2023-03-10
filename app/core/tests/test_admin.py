from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = 'admin@hosseindev.com'
        self.admin_user_password = 'test123'
        self.admin_user = User.objects.create_superuser(
            email=self.email,
            password=self.admin_user_password
        )
        self.client.force_login(self.admin_user)

        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            name="Test user full name",
        )

    def test_user_listed(self):
        """Test that user are listed on user page in admin"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
