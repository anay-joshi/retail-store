from django.db import models
from django.contrib.auth.models import User

# category of products
class Category(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.title
	
# Product description
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    price = models.IntegerField()
    stock = models.IntegerField()
    description= models.TextField(blank=True)
    status = models.BooleanField(default=True)  # in stock or not
    date_created = models.DateField(auto_now_add=True)
	
    class Meta:
        ordering = ['-date_created']
		
    def __str__(self):
        return self.name

class Cart(models.Model):
    customer = models.OneToOneField(
        User,
        related_name='cart',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s's %s "%(self.customer,'cart')


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        related_name='items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return ('%s: %s' % (self.product.name, self.quantity))


class Order(models.Model):
    customer = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='order_items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return ('%s: %s' % (self.product.name, self.quantity))