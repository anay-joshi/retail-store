from django.urls import path, include
from .views import *  
from rest_framework import routers

app_name='api'
router = routers.SimpleRouter()

router = router = routers.SimpleRouter()
router.register('categories', CategoryViewSet, 'categories')
router.register('products', ProductViewSet, 'products')
router.register('carts', CartViewSet, 'carts')
router.register('cart_items', CartItemViewSet, 'cart_items')
router.register('orders', OrderViewSet, 'orders')
router.register('order_items', OrderItemViewSet,'order_items')
router.register('analytics', AnalyticsViewSet, 'analytics')

urlpatterns = [
    path('', include((router.urls, app_name)))
]
