from django.db.models import Avg
from rest_framework import serializers

from .models import (Brand, Category, FavoriteProduct, Product, ProductImage,
                     ProductRating)

# ======================================================================================================


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug", "parent"]


# ======================================================================================================


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "title", "slug"]


# ======================================================================================================


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]


# ======================================================================================================
class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "price",
            "stock",
            "category",
            "brand",
            "main_image",
            "is_active",
        ]

    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first()
        if main:
            request = self.context.get("request")
            url = main.image.url
            return request.build_absolute_uri(url) if request else url
        return None


# =====================================================================================================


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "stock",
            "category",
            "brand",
            "images",
            "average_rating",
            "is_active",
            "created_at",
        ]

    def get_average_rating(self, obj):
        result = obj.ratings.aggregate(Avg("score"))
        return result["score__avg"]


# ======================================================================================================


class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = ["id", "user", "product", "created_at"]


# =======================================================================================================


class ProductRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductRating
        fields = ["id", "user", "product", "comment", "score", "created_at"]
        read_only_fields = ["user"]
