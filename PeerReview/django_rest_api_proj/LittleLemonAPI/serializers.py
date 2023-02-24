from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User
from datetime import datetime


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'category', 'title', 'price', 'featured']
        read_only_fields = ['category']


class UserSerializer(serializers.ModelSerializer):
    date_serial = serializers.DateTimeField(write_only=True, default=datetime.now)
    date_method = serializers.SerializerMethodField()
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_serial', 'date_method']

    def get_date_method(self, obj):
        return obj.date_serial.strftime('%Y-%m-%d')


class UserCartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    name = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = Cart
        fields = ['user_id', 'menuitem', 'name', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'price': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    name = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'menuitem': {'read_only': True}
        }


class UserOrdersSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    date_method = serializers.SerializerMethodField()
    date_serial = serializers.DateTimeField(write_only=True, default=datetime.now)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'Date', 'date_serial', 'order_items']
        extra_kwargs = {
            'total': {'read_only': True}
        }

    def get_date_method(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': self.context['request']})
        return serializer.data