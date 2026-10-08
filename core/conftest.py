import pytest
from django.contrib.auth import get_user_model
from shop.models import Category, Brand, Product
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()


@pytest.fixture
def user2(db):
    return User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass123')


@pytest.fixture
def category(db):
    return Category.objects.create(title='موبایل')


@pytest.fixture
def brand(db):
    return Brand.objects.create(title='سامسونگ')


@pytest.fixture
def product(db, category, brand):
    return Product.objects.create(
        title='گوشی تست',
        price=1000000,
        stock=10,
        category=category,
        brand=brand,
        is_active=True,
    )


@pytest.fixture
def auth_client(db, user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return client
