from django.contrib.auth import get_user_model

User=get_user_model()



class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.session.modified = True

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id] = quantity
            self.session.modified = True 

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    def decrease(self, product_id, quantity=1):
        product_id = str(product_id)
        if product_id in self.cart:
              self.cart[product_id] -= quantity
              if self.cart[product_id] <= 0:
                 del self.cart[product_id]
              self.session.modified = True

    def get_items(self):
         from .models import Product
         product_ids = self.cart.keys()
         products = Product.objects.filter(id__in=product_ids)
         items = []
         total = 0
         for product in products:
                 quantity = self.cart[str(product.id)]
                 item_total = product.price * quantity
                 total += item_total
                 items.append({'product': product,'quantity': quantity,'item_total': item_total,})
         return items, total  