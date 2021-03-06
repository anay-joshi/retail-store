from django.db.models import FloatField, Sum, F
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from datetime import datetime

from collections import defaultdict
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Endpoint to view or edit categories
    """  
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Endpoint to view or edit products
    """    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartViewSet(viewsets.ModelViewSet):
    """
    Endpoint to view or edit cart
    """ 
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=True, methods=['post', 'put'], url_path='add_to_cart')
    def add_to_cart(self, request, pk=None):

        """Add an item to a user's cart.

        Adding to cart is disallowed if there is not enough inventory for the
        product available. If there is, the quantity is increased on an existing
        cart item or a new cart item is created with that quantity and added
        to the cart.

        """

        cart = self.get_object()
        try:
            product = Product.objects.get(
                pk=request.data['product_id']
            )
            quantity = int(request.data['quantity'])
        except Exception as e:
            print(e)
            return Response({'status': 'fail'})

        if product.stock <= 0 or product.stock - quantity < 0:
            print("Amount of products not available")
            return Response({'status': 'fail', 'message':'Amount of products not available'})

        existing_cart_item = CartItem.objects.filter(cart=cart,product=product).first()

        if existing_cart_item:
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
        else:
            new_cart_item = CartItem(cart=cart, product=product, quantity=quantity)
            new_cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'put'], url_path='remove_from_cart')
    def remove_from_cart(self, request, pk=None):

        """ Remove an item from a user's cart.

        If the quantity of the product to remove from the cart is 1, 
        delete the cart item. If the quantity is more than 1, decrease
        the quantity of the cart item according to the quantity mentioned,
        but leave it in the cart.
        If quantity is not specified, decrease by 1.

        """

        cart = self.get_object()
        try:
            product = Product.objects.get(
                pk=request.data['product_id']
            )
        except Exception as e:
            print(e)
            return Response({'status': 'fail'})

        try:
            cart_item = CartItem.objects.get(cart=cart,product=product)
        except Exception as e:
            print(e)
            return Response({'status': 'fail'})

        if cart_item.quantity == 1 or cart_item.quantity<request.data['quantity'] :
            cart_item.delete()
        elif cart_item.quantity>request.data['quantity'] :
            cart_item.quantity -= request.data['quantity']
            cart_item.save()
        else:
            cart_item.quantity -= 1
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    Endpoint to view all carts
    """ 

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class OrderViewSet(viewsets.ModelViewSet):

    """
    Endpoint to view all order related functionalities
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):

        try:
            purchaser_id = self.request.data['purchaser']
            user = User.objects.get(pk=purchaser_id)
        except:
            raise serializers.ValidationError(
                'User was not found'
            )

        cart = user.cart

        for cart_item in cart.items.all():
            if cart_item.product.stock - cart_item.quantity < 0:
                raise serializers.ValidationError(
                    'Sorry we only have '+str(cart_item.product.stock)+' items and cannot place your order of '+
                    str(cart_item.quantity)+' items.'
                )

        total_aggregated_dict = cart.items.aggregate(total=Sum(F('quantity')*F('product__price'),output_field=FloatField()))

        order_total = round(total_aggregated_dict['total'], 2)
        order = serializer.save(customer=user, total=order_total)

        order_items = []
        for cart_item in cart.items.all():
            order_items.append(OrderItem(order=order, product=cart_item.product, quantity=cart_item.quantity))
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()


        OrderItem.objects.bulk_create(order_items)
        cart.items.clear()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    """
    Endpoint to view complete order history
    """

    @action(detail=False, url_path="order_history/(?P<customer_id>[0-9])")
    def order_history(self, request, customer_id):

        try:
            user = User.objects.get(id=customer_id)

        except:
            return Response({'status': 'fail'})

        orders = Order.objects.filter(customer=user)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)

class OrderItemViewSet(viewsets.ModelViewSet):

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class AnalyticsViewSet(viewsets.GenericViewSet):

    """
    Endpoint for questions 3 and 4
    """

    """
    1. No of transactions with option of adding date range
    """
    @action(detail=False, url_path="total_orders")
    def total_transactions(self, request):
        # print(request.data)
        if not request.data or ( not request.data['start_date'] ) or ( not request.data['end_date']): 
            count = Order.objects.all().count()    
        else:
            start_date=request.data['start_date']
            end_date=request.data['end_date']
            count = Order.objects.filter(created_at__range=[start_date,end_date]).count()
            
        return Response({'Total Number of Orders ':count})

    """
    2. Fetching total quantity of all items sold with options of adding date range
    """
    @action(detail=False, url_path="total_quantity_sold")
    def total_quantity(self, request):
        orderitems = OrderItem.objects.all()    
        quantity=0

        if not request.data or ( not request.data['start_date'] ) or ( not request.data['end_date']):        
            for item in orderitems:
                quantity += item.quantity

        else:
            start_date=request.data['start_date']
            end_date=request.data['end_date']
            for item in orderitems: 
                # print(start_date,str(item.order.created_at) , end_date)
                if start_date <= str(item.order.created_at)  <= end_date:
                    quantity += item.quantity

        return Response({'Total Quantity of items sold ':quantity})

    """
    3. total quantity sold for each item with option of adding date range
    """
    @action(detail=False, url_path="per_item_quantity_sold")
    def per_item_quantity(self, request):
        orderitems = OrderItem.objects.all()
        response={}

        if not request.data or ( not request.data['start_date'] ) or ( not request.data['end_date']):
            for item in orderitems:
                response[item.product.name] = item.quantity
        
        else:
            start_date=request.data['start_date']
            end_date=request.data['end_date']
            for item in orderitems: 
                # print(start_date,str(item.order.created_at) , end_date)
                if start_date <= str(item.order.created_at)  <= end_date:
                    response[item.product.name] = item.quantity

        return Response(response)

    """
    4. total quantity sold in each item category with option of adding date range
    """
    @action(detail=False, url_path="per_category_item_quantity_sold")
    def per_category_quantity(self, request):
        orderitems = OrderItem.objects.all()
        response= defaultdict(lambda: 0)

        if not request.data or ( not request.data['start_date'] ) or ( not request.data['end_date']):
            for item in orderitems:
                response[str(item.product.category)] += 1

        else:
            start_date=request.data['start_date']
            end_date=request.data['end_date']
            for item in orderitems: 
                # print(start_date,str(item.order.created_at) , end_date)
                if start_date <= str(item.order.created_at)  <= end_date:
                    response[str(item.product.category)] += 1

        return Response(response)


    """
    5. total sales amount with option of adding date range
    """
    @action(detail=False, url_path="total_amount")
    def total_amount(self, request):
        orders=Order.objects.all()
        total_amount=0
        response= {}

        if not request.data or ( not request.data['start_date'] ) or ( not request.data['end_date']):
            for order in orders:
                k="Sale amount of order no. : %s" % (order.id)
                response[k]=order.total
                total_amount += order.total
        
        else:
            start_date=request.data['start_date']
            end_date=request.data['end_date']
            for order in orders:
                # print(start_date,str(item.order.created_at) , end_date)
                if start_date <= str(order.created_at)  <= end_date:
                    k="Sale amount of order no. : %s" % (order.id)
                    response[k]=order.total
                    total_amount += order.total

        response["Total Sales Amount"]=total_amount
        return Response(response)

    
                                
        
        




