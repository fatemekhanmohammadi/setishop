from django.test import TestCase
import pytest
from rest_framework.test import APIClient
from django.test import Client
from decimal import Decimal
from django.contrib.auth import get_user_model
from cart.models import Cart, CartItem, Order, OrderItem
User=get_user_model()

#==========================================================================================================================
@pytest.mark.django_db
def test_add_to_cart_session(product):
    client = APIClient()
    response = client.post('/shop/api/cart/add/', {'product_id': product.id, 'quantity': 2}, format='json')
    assert response.status_code == 201

#==========================================================================================================================
@pytest.mark.django_db
def test_cart_merge_on_login(client, user, product):
    django_client = Client()

    session = django_client.session
    session['cart'] = {str(product.id): 3}
    session.save()

    response = django_client.post('/accounts/api/token/', {'username': user.username,'password': 'testpass123'}, content_type='application/json')

    assert response.status_code == 200
    cart = Cart.objects.filter(user=user).first()
    assert cart is not None
    assert cart.cartitem_set.filter(product=product).exists()

#==========================================================================================================================

@pytest.mark.django_db
def test_checkout_success(auth_client, user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    response = auth_client.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json')
    assert response.status_code == 201
    product.refresh_from_db()
    assert product.stock == 8  # 10 - 2

    assert not CartItem.objects.filter(cart=cart).exists()
#=========================================================================================================================

@pytest.mark.django_db
def test_checkout_insufficient_stock(auth_client, user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=100)

    response = auth_client.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json')

    assert response.status_code == 400
    product.refresh_from_db()
    assert product.stock == 10  # هیچی کم نشده

#==========================================================================================================================
@pytest.mark.django_db
def test_checkout_empty_cart(auth_client, user):
    response = auth_client.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json')
    assert response.status_code == 400


#==========================================================================================================================



@pytest.mark.django_db
def test_checkout_total_and_price_at_purchase(auth_client, user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=3)
    response = auth_client.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json')
    assert response.status_code == 201
    order = Order.objects.get(id=response.data['order_id'])
    assert order.status == 'PENDING'
    assert order.total_price == product.price * 3 + 50000
    assert order.items.get().price_at_purchase == product.price
#==========================================================================================================================

@pytest.mark.django_db
def test_price_is_frozen_after_price_change(auth_client, user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    response = auth_client.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json')
    old_price = product.price
    product.price = old_price + 5000
    product.save()
    item = OrderItem.objects.get(order_id=response.data['order_id'])
    assert item.price_at_purchase == old_price
#==========================================================================================================================

@pytest.mark.django_db
def test_checkout_failure_creates_no_order(auth_client, user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=100)
    auth_client.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json')
    assert Order.objects.count() == 0
    assert CartItem.objects.filter(cart=cart).count() == 1

#==========================================================================================================================
@pytest.mark.django_db
def test_last_item_goes_to_first_buyer_only(user, product):
    product.stock = 1
    product.save()
    other = get_user_model().objects.create_user(username='other', password='testpass123')
    results = []
    for u in (user, other):
        cart = Cart.objects.create(user=u)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        c = APIClient()
        c.force_authenticate(user=u)
        results.append(c.post('/cart/api/orders/checkout/', {'address': 'تهران'}, format='json').status_code)
    product.refresh_from_db()
    assert results == [201, 400]
    assert product.stock == 0


def _login_with_session_cart(user, product, qty):
    c = Client()
    session = c.session
    session['cart'] = {str(product.id): qty}
    session.save()
    response = c.post('/accounts/api/token/', {'username': user.username, 'password': 'testpass123'}, content_type='application/json')
    return c, response

#==========================================================================================================================
@pytest.mark.django_db
def test_merge_keeps_max_quantity_session_bigger(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    _login_with_session_cart(user, product, 7)
    assert CartItem.objects.get(cart=cart, product=product).quantity == 7

#==========================================================================================================================
@pytest.mark.django_db
def test_merge_keeps_max_quantity_db_bigger(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=5)
    _login_with_session_cart(user, product, 3)
    assert CartItem.objects.get(cart=cart, product=product).quantity == 5
#==========================================================================================================================

@pytest.mark.django_db
def test_merge_clears_session_cart(user, product):
    c, _ = _login_with_session_cart(user, product, 3)
    assert 'cart' not in c.session


#==========================================================================================================================