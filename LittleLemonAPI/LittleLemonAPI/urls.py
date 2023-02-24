
# Django
from django.urls import path, include

# Views
from . import views

# DRF
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register('menu-items', views.MenuItems)
urlpatterns = router.urls

urlpatterns += [
    # Authtoken
    path('token', obtain_auth_token),

    # Djoser - User registration and token generation endpoints 
    path('auth', include('djoser.urls')),
    path('auth', include('djoser.urls.authtoken')),

    # Menu-items endpoints
    #path('menu-items', views.MenuItems.as_view(), name='' ), --> routers
    #path('/api/menu-items/<int:menuItem>', name='' ),

    # User group management endpoints
    path('groups/manager/users', views.ManagerGroup.as_view(), name='' ),
    path('groups/manager/users/<int:userId>', views.ManagerGroup.as_view(), name='' ),
    path('groups/delivery-crew/users', views.delivery_crew_group, name='' ),
    path('groups/delivery-crew/users/<int:userId>', views.delete_delivery_crew, name='' ),

    # Cart management endpoints
    path('cart/menu-items', views.Carts.as_view(
        {
            'get': 'list',
            'post': 'create',
            'delete': 'destroy'
        }), name='' ),

    # Order management endpoints
    path('orders', views.Orders.as_view(), name='' ),
    path('orders/<int:orderId>', views.SingleOrder.as_view(), name='' ),
]