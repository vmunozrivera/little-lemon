from django.shortcuts import render, get_object_or_404
from django.http import request
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Category,MenuItem,Order,Cart, OrderItem
from .serializers import CategorySerializer,MenuItemSerializer,CartSerializer,UserSerializer,OrderSerializer,OrderItemSerializer
from django.contrib.auth.models import User, Group
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.paginator import Paginator, EmptyPage

# Create your views here.
@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == 'GET':
        group = Group.objects.get(name='Manager')
        users = group.user_set.all()
        serializer = UserSerializer(users,many=True)
        return Response(serializer.data)
    username =request.data['Username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        if request.method =='POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({'message':'ok'})
    return Response({'message':'error'}, status =status.HTTP_400_BAD_REQUEST)
            
        
    
@api_view(['GET','DELETE'])
@permission_classes([IsAdminUser])
def managerdetail(request,pk):
    if request.method == 'GET':
        group = Group.objects.get(name='Manager')
        users = group.user_set.get(id=pk)
        serializer = UserSerializer(users,many=False)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        group = Group.objects.get(name='Manager')
        users = group.user_set.get(id=pk)
        users.delete()
        return Response('User was successfully deleted')
    
@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def delivery_crew(request):
    if request.method == 'GET':
        group = Group.objects.get(name='Delivery Crew')
        users = group.user_set.all()
        serializer = UserSerializer(users,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        username =request.data['Username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            if request.method =='POST':
                delivery_crew.user_set.add(user)
            elif request.method == 'DELETE':
                delivery_crew.user_set.remove(user)
            return Response({'message':'ok'}, status=status.HTTP_200_OK)
        return Response({'message':'error'}, status =status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def deliverydetail(request,pk):
    if request.method == 'GET':
        group = Group.objects.get(name='Delivery Crew')
        users = group.user_set.get(id=pk)
        serializer = UserSerializer(users,many=False)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        group = Group.objects.get(name='Delivery Crew')
        users = group.user_set.get(id=pk)
        users.delete()
        return Response({'message':'User was successfully deleted'})



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def menu_itemsView(request):
    if request.method == 'GET':
        menu = MenuItem.objects.all()
        
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        singlepage = request.query_params.get('singlepage',default=3)
        page = request.query_params.get('page', default = 1)
        ordering = request.query_params.get('ordering')

        if category_name:
            menu = menu.filter(category__title = category_name)
        if to_price:
            menu = menu.filter(price__lte = to_price)
        if search:
            menu = menu.filter(title__icontains = search)
        if ordering:
            ordering_fields = ordering.split(",")
            menu = menu.order_by(*ordering_fields)
        paginator = Paginator(menu,per_page=singlepage)
        try:
            menu = paginator.page(number=page)
        except EmptyPage:
            menu =[]
        serializer = MenuItemSerializer(menu, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    elif request.method == 'POST':
        if request.user.groups.filter(name='Manager').exists():
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'ok'}, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
        else:
            return Response({'message':'You are not authorized'}, status = status.HTTP_403_FORBIDDEN)
   

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def category(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer=CategorySerializer(categories,many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
    elif request.method == 'POST':
        if request.user.groups.filter(name='Manager').exists():
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'ok'}, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
        else:
            return Response({'message':'You are not authorized'}, status = status.HTTP_403_FORBIDDEN)
        
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def menu_itemsDetails(request,pk):
    if request.method == 'GET':
        menu = MenuItem.objects.get(id=pk)
        serializer = MenuItemSerializer(menu, many=False)
        return Response(serializer.data, status = status.HTTP_200_OK)
    elif request.method == 'POST':
        if request.user.groups.filter(name='Manager').exists():
            serializer = MenuItemSerializer(request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'ok'}, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
        else:
            return Response({'message':'You are not authorized'}, status = status.HTTP_403_FORBIDDEN)
    elif request.method == 'PUT':
        if request.user.groups.filter(name='Manager').exists():
            menu = MenuItem.objects.get(id=pk)
            serializer = MenuItemSerializer(instance=menu, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'ok'}, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
        else:
            return Response({'message':'You are not authorized'}, status = status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
           menu = MenuItem.objects.get(id=pk)
           menu.delete()
           return Response('Item was successfully deleted')
        else:
            return Response({'message':'You are not authorized'}, status = status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST','DELETE'])
@permission_classes([IsAuthenticated])
def cart_itemsView(request):
    if request.method == 'GET':
        cart = Cart.objects.all()
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CartSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Items added successfully'}, status = status.HTTP_201_CREATED)
        else:
            return Response({'message':'Invalid entry'})
    elif request.method == 'DELETE':
        cart = Cart.objects.all()
        cart.delete()
        return Response('Items in the cart were successfully deleted')

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders(request):
    if request.method == 'GET':
        order = Order.objects.all()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    elif request.method == 'POST':
            serializer = OrderSerializer(request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
            

@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def orderDetails(request,pk):
    if request.method == 'GET':
        order = Order.objects.get(id=pk)
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data, status = status.HTTP_200_OK)
    elif request.method == 'POST':
            serializer = OrderSerializer(request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'ok'}, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
        
    elif request.method == 'PUT':
            order = Order.objects.get(id=pk)
            serializer = OrderSerializer(instance=order, data= request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'updated'}, status = status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid entry'})
            
    elif request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
           menu = MenuItem.objects.get(id=pk)
           menu.delete()
           return Response('Item was successfully deleted')
        else:
            return Response({'message':'You are not authorized'}, status = status.HTTP_403_FORBIDDEN)

   


            


