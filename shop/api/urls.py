from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.registration),
    path('login', views.login),
    path('logout', views.logout),
    path('products', views.get_products),
    path('cart/<int:pk>', views.add_delete_to_cart),
    path('cart', views.get_cart),
    path('order', views.get_create_order),
    path('product', views.create_product),
    path('product/<int:pk>', views.edit_delete_product)
]
