from django.contrib import admin
from django.contrib.auth import get_user_model
User=get_user_model()
from .models import Category, Brand, Product, ProductImage,FavoriteProduct



#===============================================================================

class ProductImageInline(admin.TabularInline):      
    model = ProductImage
    extra = 1

#===============================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'stock', 'category', 'is_active']
    inlines = [ProductImageInline]

#===============================================================================

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(FavoriteProduct)