from django.urls import path
from . import views

urlpatterns = [
    path('menu_items/',views.menu_itemsView, name='menu_items'),
    path('menu_items/<int:pk>',views.menu_itemsDetails, name='menu_itemsdetails'),
    path('groups/managers/users/', views.managers, name='managers'),
    path('groups/managers/users/<int:pk>', views.managerdetail,name='managerdetail'),
    path('groups/delivery_crew/users/', views.delivery_crew,name='delivery_crew'),
    path('groups/delivery_crew/users/<int:pk>',views.deliverydetail,name='deliverydetail'),
    path('cart/menu-items/',views.cart_itemsView,name='cart-items'),
    path('orders/',views.orders,name='orders'),
    path('orders/<int:pk>',views.orderDetails,name='orders'),
    path('categories/',views.category,name='category'),


]