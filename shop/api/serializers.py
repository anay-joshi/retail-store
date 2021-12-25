from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category 
        fields = (
            'id',
            'title'
        )
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'category',
            'price',
            'stock',
			'description',
            'status',
            'date_created'
        )
        

class CartSerializer(serializers.ModelSerializer):

    customer = UserSerializer(read_only=True)
    items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Cart
        fields = (
            'id', 
            'customer', 
            'created_at', 
            'updated_at', 
            'items'
        )

class CartItemSerializer(serializers.ModelSerializer):

    cart = CartSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = (
            'id', 
            'cart', 
            'product', 
            'quantity'
        )


class OrderSerializer(serializers.ModelSerializer):

    customer = UserSerializer(read_only=True)
    order_items = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Order
        fields = (
            'id', 
            'customer', 
            'total', 
            'created_at', 
            'updated_at', 
            'order_items'
        )

    def create(self, validated_data):
 
        order = Order.objects.create(**validated_data)
        return order

class OrderItemSerializer(serializers.ModelSerializer):

    order = OrderSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id', 
            'order', 
            'product', 
            'quantity'
        )
