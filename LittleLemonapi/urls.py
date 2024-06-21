from django.urls import path
from .views import menu_items, menu_item_detail
from .import views


urlpatterns = [
    path('menu-items/', menu_items, name='menu_items'),
    path('menu-items/<int:pk>/', menu_item_detail, name='menu_item_detail'),
    path('groups/manager/users', views.manager_group, name='manager_group'),
    path('groups/manager/users/<int:user_id>', views.remove_manager, name='remove_manager'),
    path('groups/delivery-crew/users', views.delivery_crew_group, name='delivery_crew_group'),
    path('groups/delivery-crew/users<int:user_id>', views.remove_delivery_crew, name='remove_delivery_crew'),
    path('cart/menu-items', views.cart_menu_items, name='cart_menu_items'),
    path('orders', views.customer_orders, name='customer_orders'),
    path('orders/<int:order_id>', views.order_detail, name='order_detail'),
    path('manager/orders', views.manager_orders, name='manager_orders'),
    path('delivery-crew/orders', views.delivery_crew_orders, name='delivery_crew_orders'),
    path('delivery-crew/orders/<int:order_id>', views.delivery_crew_orders, name='delivery_crew_order_detail'),
    path('cart/menu-items', views.cart_menu_items, name='cart_menu_items'),
]

