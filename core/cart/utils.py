from .models import Cart, CartItem


#===========================================================================================================

def merge_session_cart_to_db(request, user):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return
    cart, created = Cart.objects.get_or_create(user=user)
    for product_id, quantity in session_cart.items():
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart,product_id=product_id,defaults={'quantity': quantity})
        if not item_created:
            # تصمیم: به‌جای جمع کردن، بیشترین مقدار quantity نگه داشته می‌شه
            cart_item.quantity = max(cart_item.quantity, quantity)
            cart_item.save()
    del request.session['cart']
    request.session.modified = True

#===========================================================================================================