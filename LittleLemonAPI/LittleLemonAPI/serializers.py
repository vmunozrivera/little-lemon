
# python
from decimal import Decimal

# DRF 
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

# Models
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class CartSerializer(ModelSerializer):
    # user = serializers.IntegerField()
    # menu_item = serializers.IntegerField()
    # quantity = serializers.IntegerField()
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    class Meta:
        model = Cart
        fields = ['user', 'menu_item', 'quantity', 'unit_price', 'price', 'price_with_tax']
    
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_price')
 
    def calculate_price(self, item:Cart):
        print(item.price)
        return item.price * Decimal(1.18)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = MenuItem
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']