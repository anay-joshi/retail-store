from django.urls import path, include
from .views import *  
from rest_framework import routers

app_name='api'
router = routers.SimpleRouter()

router = router = routers.SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('carts', CartViewSet)
router.register('cart_items', CartItemViewSet)
router.register('orders', OrderViewSet)
router.register('order_items', OrderItemViewSet)

urlpatterns = [
    path('', include((router.urls, app_name)))
]
