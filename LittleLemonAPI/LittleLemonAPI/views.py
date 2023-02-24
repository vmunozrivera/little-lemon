
# Django
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage #Pagination

# DRF
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication

from rest_framework.pagination import PageNumberPagination

from rest_framework.throttling import AnonRateThrottle

# Models
from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, Order
from .serializers import OrderSerializer, MenuItemSerializer, CartSerializer
from .serializers import UserSerializer, OrderItemSerializer


# Orders (Generic Views)
@throttle_classes([AnonRateThrottle])
@permission_classes([IsAuthenticated])
class Orders(ListCreateAPIView):
    """ Order management - List and Create"""

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager'):
            queryset = Order.objects.select_related('user').all()
            # Search
            search = self.request.query_params.get('search')
            print(search)
            if search:
                queryset = queryset.filter(status=search)
        if self.request.user.groups.filter(name='Delivery crew'):
            queryset = Order.objects.exclude(delivery_crew__isnull=True).exclude(delivery_crew__exact='')
        else:
            queryset = Order.objects.all().filter(user=self.request.user.id)
            #queryset = Order.objects.select_related('user').all().filter(user=1)

            # Search
            search = self.request.query_params.get('search')
            print(search)
            if search:
                queryset = queryset.filter(status=search)

            # Ordering
            ordering = self.request.query_params.get('ordering')
            if ordering:
                queryset = queryset.order_by(ordering)
                # Multiple values
                # ordering_fields = ordering.split(",")
                # queryset = queryset.order_by(*ordering_fields)

            # Pagination
            perpage = self.request.query_params.get('perpage', default=2)
            
            page = self.request.query_params.get('page', default=1)
            paginator = Paginator(queryset, per_page=perpage)
            print(paginator)
            try:
                queryset = paginator.page(number=page)
            except EmptyPage:
                queryset = []

        return queryset
    
    def get_serializer_class(self):
        return OrderSerializer
    
    def post(self, request, *args, **kwargs):
        """ Creates a new order item for the current user. 
        Gets current cart items from the cart endpoints and adds those items to the order items table. 
        Then deletes all items from the cart for this user. """
        
        # Create Order
        current_user = request.user
        user_id = current_user.id
        request.data["user"] = user_id
        #request.data['user'] = 1

        create_order = super().post(request, *args, **kwargs)
        
        # Move items from cart
        #data = Carts.as_view({'get': 'list'})(request._request).data
        #cart = Cart.objects.all().filter(user=self.request.user.id)
        cart_items = Cart.objects.all().filter(user=1)
        new_order_item = {}
        for item in cart_items:
            new_order_item['order'] = create_order.data['id']
            new_order_item['menu_item'] = item.menu_item.id
            new_order_item['quantity'] = item.quantity
            new_order_item['unit_price'] = item.unit_price
            new_order_item['price'] = item.price
            serializer = OrderItemSerializer(data=new_order_item)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Delete cart
        cart_items.delete()
        return Response(create_order.data)

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return []
    #     return [IsAuthenticated()]

    # def get_permissions(self):
    #     permission_classes = []
    #     if self.request.method == 'GET':
    #         permission_classes = [IsAuthenticated]

    #     return [permission() for permission in permission_classes]


@throttle_classes([AnonRateThrottle])
@permission_classes([IsAuthenticated])
class SingleOrder(RetrieveUpdateDestroyAPIView):
    """ Order management - Retrieve, Update and destroy a single order"""

    serializer_class = OrderSerializer
    
    def get_queryset(self, id):
        order = Order.objects.get(pk=id)
        
        if order['user'] is not self.request.user.id:
            return status.HTTP_403_FORBIDDEN
        
        return order  

    def destroy(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager'):
            return super().destroy(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager'):
            return super().partial_update(request, *args, **kwargs)
        
        if self.request.user.groups.filter(name='Delivery crew'):
            status = self.request.POST.get('status')
            
            if status:
                request[status] = 0
            else:
                request[status] = 1

            return super().partial_update(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager'):
            return super().update(request, *args, **kwargs)
    

# Cart (ViewSets - ViewSet)
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle])
class Carts(ViewSet):
    """ Cart management """
    def list(self, request):
        """ Returns current items in the cart for the current user token """
        cart = Cart.objects.all().filter(user=self.request.user.id)
        #cart = Cart.objects.prefetch_related('menu_item').all().filter(user=1)
        print(cart)
        if not cart:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart, many=True)

        return Response(serializer.data, status.HTTP_200_OK)

    def create(self, request):
        """ Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items """
        current_user = request.user
        user_id = current_user.id

        request.data["user"] = user_id
        #request.data["user"] = 1
        request.data["price"] = request.data["quantity"] * request.data["unit_price"]
        serializer = CartSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        """ Deletes all menu items created by the current user token """
        cart = Cart.objects.all().filter(user=self.request.user.id)
        #cart = Cart.objects.all().filter(user=1)

        if not cart:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cart.delete()

        return Response(status.HTTP_204_NO_CONTENT)


# Custom Pagination Class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1000

# Menu-items (ViewSets - ModelViewSet)
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle])
class MenuItems(ModelViewSet):
    """ Menu Items """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated,]
    pagination_class = StandardResultsSetPagination
    ordering_fields=['-price']
    search_fields=['title']
    authentication_classes = (TokenAuthentication,) 

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager'):
            return super().create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager'):
            return super().update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager'):
            return super().partial_update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager'):
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def filter_queryset(self, queryset):
        queryset = super(MenuItems, self).filter_queryset(queryset)
        return queryset.order_by('-price')


# User Group - Manager (Class Based Views)
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle])
class ManagerGroup(APIView):
    def get(self, request):
        """ Returns all managers """
        if self.request.user.groups.filter(name='Manager'):
            queryset = User.objects.filter(groups__name='Manager')
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        """ Assigns the user in the payload to the manager group 
        and returns 201-Created """
        if self.request.user.groups.filter(name='Manager'):
            #new_user = User.objects.get(pk=request.data.get('user_id'))
            new_user = get_object_or_404(User, pk=request.data.get('user_id'))
            manager_group = Group.objects.get(name='Manager') 
            manager_group.user_set.add(new_user)

            return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, userId):
        """ Removes this particular user from the manager group and 
        returns 200 - Success if everything is okay.
        If the user is not found, returns 404 - Not found """
        if self.request.user.groups.filter(name='Manager'):
            user = get_object_or_404(User, pk=userId)
            manager_group = Group.objects.get(name='Manager') 
            manager_group.user_set.remove(user)

            return Response(status=status.HTTP_200_OK)


# User Group - Delivery Crew (Function Based Views)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle])
def delivery_crew_group(request):
    if request.method == 'GET':
        """ Returns all delivery crew """
        if request.user.groups.filter(name='Manager'):
            queryset = User.objects.filter(groups__name='Delivery crew')
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        """ Assigns the user in the payload to delivery crew group 
        and returns 201-Created HTTP """
        if request.user.groups.filter(name='Manager'):
            new_user = get_object_or_404(User, pk=request.data.get('user_id'))
            manager_group = Group.objects.get(name='Delivery crew') 
            manager_group.user_set.add(new_user)

            return Response(status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_delivery_crew(request, userId):
    """ Removes this user from the manager group and 
    returns 200 - Success if everything is okay.
    If the user is not found, returns  404 - Not found """
    #if request.user.groups.filter(name='Manager'):
    user = get_object_or_404(User, pk=userId)
    manager_group = Group.objects.get(name='Delivery crew') 
    manager_group.user_set.remove(user)

    return Response(status=status.HTTP_200_OK)
