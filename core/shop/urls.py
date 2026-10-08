from django.urls import path

from . import views

urlpatterns = [
    path("api/products/", views.ProductListView.as_view(), name="products"),
    path(
        "api/products/<str:slug>/",
        views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    path("api/categories/", views.CategoryListView.as_view(), name="categories"),
    path("api/cart/", views.CartDetailView.as_view(), name="cart-detail"),
    path("api/cart/add/", views.CartAddView.as_view(), name="cart-add"),
    path(
        "api/cart/update/<int:product_id>/",
        views.CartUpdateView.as_view(),
        name="cart-update",
    ),
    path(
        "api/cart/remove/<int:product_id>/",
        views.CartRemoveView.as_view(),
        name="cart-remove",
    ),
    path(
        "api/products/<int:product_id>/rate/",
        views.ProductRatingView.as_view(),
        name="product-rate",
    ),
    # فقط برای ادمین
    path(
        "api/admin/products/",
        views.AdminProductCreateView.as_view(),
        name="admin-product-create",
    ),
    path(
        "api/admin/products/<int:pk>/",
        views.AdminProductUpdateView.as_view(),
        name="admin-product-update",
    ),
    path(
        "api/admin/products/<int:pk>/delete/",
        views.AdminProductDeleteView.as_view(),
        name="admin-product-delete",
    ),
    path("api/favorites/", views.FavoriteProductView.as_view(), name="favorites-list"),
    path(
        "api/favorites/<int:product_id>/",
        views.FavoriteProductView.as_view(),
        name="favorites-detail",
    ),
]
