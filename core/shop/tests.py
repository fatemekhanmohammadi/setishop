from .models import ProductRating
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()


# ============================================
# Rating
# ============================================
@pytest.mark.django_db
def test_first_rating_success(auth_client, user, product):
    url = reverse('product-rate', kwargs={'product_id': product.pk})
    response = auth_client.post(
        url, {'score': 4, 'comment': 'خوب بود'}, format='json')
    assert response.status_code == 201
    assert ProductRating.objects.filter(
        user=user, product=product).count() == 1


@pytest.mark.django_db
def test_second_rating_same_user_rejected(auth_client, user, product):
    url = reverse('product-rate', kwargs={'product_id': product.pk})
    auth_client.post(url, {'score': 4, 'comment': 'خوب بود'}, format='json')
    response = auth_client.post(
        url, {'score': 1, 'comment': 'بد بود'}, format='json')
    assert response.status_code == 400
    assert ProductRating.objects.filter(
        user=user, product=product).count() == 1
    assert ProductRating.objects.get(user=user, product=product).score == 4


@pytest.mark.django_db
def test_different_users_can_rate_same_product(
        api_client, user, admin_user, product):
    url = reverse('product-rate', kwargs={'product_id': product.pk})
    api_client.force_authenticate(user=user)
    assert api_client.post(url, {'score': 4}, format='json').status_code == 201
    api_client.force_authenticate(user=admin_user)
    assert api_client.post(url, {'score': 5}, format='json').status_code == 201
    assert ProductRating.objects.filter(product=product).count() == 2


# ============================================
# ============================================
