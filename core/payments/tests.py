from django.test import TestCase
import pytest
from unittest.mock import patch
from payments.models import Payment
from cart.models import Order

# ==========================================================================================================================


@pytest.mark.django_db
def test_payment_verify_idempotent(auth_client, user, product):
    order = Order.objects.create(
        user=user, address='تهران', total_price=1000000)
    payment = Payment.objects.create(
        order=order, amount=1000000, authority='S123', status='PAID', ref_id='REF1')

    response = auth_client.get('/payments/api/payments/verify/?Authority=S123')

    assert response.status_code == 200
    assert 'قبلاً' in response.data['message']

# ==========================================================================================================================


@pytest.mark.django_db
@patch('payments.views.requests.post')
def test_payment_verify_success(mock_post, auth_client, user):
    order = Order.objects.create(
        user=user, address='تهران', total_price=1000000)
    payment = Payment.objects.create(
        order=order, amount=1000000, authority='S456', status='PENDING')

    mock_post.return_value.json.return_value = {
        'data': {'code': 100, 'ref_id': 'REF999'}
    }

    response = auth_client.get('/payments/api/payments/verify/?Authority=S456')

    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == 'PAID'
    assert payment.ref_id == 'REF999'


# ==========================================================================================================================

@pytest.mark.django_db
@patch('payments.views.requests.post')
def test_verify_marks_order_paid(mock_post, auth_client, user):
    order = Order.objects.create(
        user=user, address='تهران', total_price=1000000)
    Payment.objects.create(order=order, amount=1000000,
                           authority='S1', status='PENDING')
    mock_post.return_value.json.return_value = {
        'data': {'code': 100, 'ref_id': 'REF1'}}
    auth_client.get('/payments/api/payments/verify/?Authority=S1')
    order.refresh_from_db()
    assert order.status == 'PAID'

# ==========================================================================================================================


@pytest.mark.django_db
@patch('payments.views.requests.post')
def test_verify_twice_calls_gateway_once(mock_post, auth_client, user, product):
    order = Order.objects.create(
        user=user, address='تهران', total_price=1000000)
    Payment.objects.create(order=order, amount=1000000,
                           authority='S2', status='PENDING')
    mock_post.return_value.json.return_value = {
        'data': {'code': 100, 'ref_id': 'REF2'}}
    url = '/payments/api/payments/verify/?Authority=S2'
    assert auth_client.get(url).status_code == 200
    assert auth_client.get(url).status_code == 200
    assert mock_post.call_count == 1
    product.refresh_from_db()
    assert product.stock == 10

# ==========================================================================================================================


@pytest.mark.django_db
@patch('payments.views.requests.post')
def test_verify_failed_payment(mock_post, auth_client, user):
    order = Order.objects.create(
        user=user, address='تهران', total_price=1000000)
    payment = Payment.objects.create(
        order=order, amount=1000000, authority='S3', status='PENDING')
    mock_post.return_value.json.return_value = {'data': {'code': 101}}
    response = auth_client.get('/payments/api/payments/verify/?Authority=S3')
    assert response.status_code == 400
    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == 'FAILED'
    assert order.status == 'PENDING'

# ==========================================================================================================================


@pytest.mark.django_db
def test_verify_unknown_authority(auth_client):
    response = auth_client.get('/payments/api/payments/verify/?Authority=NOPE')
    assert response.status_code == 404


# ==========================================================================================================================
