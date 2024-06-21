from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, Category, MenuItem, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, CategorySerializer, OrderItemSerializer, OrderSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group





@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == 'GET':

        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not request.user.groups.filter(name='managers').exist():
            return Response({'Detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item_detail(request, pk):

    item = get_object_or_404(MenuItem, pk=pk)

    if request.method == 'GET':
        serializer = MenuItemSerializer(item)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH', 'DELETE']:
        # Only allow managers to update or delete menu items
        if not request.user.groups.filter(name='managers').exists():
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'DELETE':
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


        serializer = MenuItemSerializer(item, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

api_view(['GET', 'POST'])
permission_classes([IsAuthenticated])
def manager_group(request):
    
    if not request.user.groups.filter(name='managers').exists():
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
         managers = User.objects.filter(groups__name='managers')
         manager_data = [{'id': manager.id, 'username': manager.username} for manager in managers]
         return Response(manager_data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)
        manager_group, created = Group.objects.get_or_create(name='managers')
        manager_group.user_set.add(user)
        return Response({"detail": "User added to manager group"}, status=status.HTTP_201_CREATED)

        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_manager(request, user_id):
    if not request.user.groups.filter(name='managers').exists():
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
        manager_group = Group.objects.get(name='managers')
        manager_group.user_set.remove(user)
        return Response({"detail": "User removed from manager group"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_crew_group(request):
    if not request.user.groups.filter(name='managers').exists():
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        delivery_crew = User.objects.filter(groups__name='delivery_crew')
        delivery_crew_data = [{'id': member.id, 'username': member.username} for member in delivery_crew]
        return Response(delivery_crew_data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)
        delivery_crew_group, created = Group.objects.get_or_create(name='delivery_crew')
        delivery_crew_group.user_set.add(user)
        return Response({"detail": "User added to delivery crew group"}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_delivery_crew(request, user_id):
    if not request.user.groups.filter(name='managers').exists():
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
        delivery_crew_group = Group.objects.get(name='delivery_crew')
        delivery_crew_group.user_set.remove(user)
        return Response({"detail": "User removed from delivery crew group"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    if request.method == 'GET':
        cart_items = Cart.objects.filter(user=request.user)
        data = [
            {
                "id": item.id,
                "menuitem": item.menuitem.title,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.quantity * item.unit_price,
            }
            for item in cart_items
        ]
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        menuitem_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity', 1)

        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, menuitem=menuitem, defaults={'quantity': quantity, 'unit_price': menuitem.price}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response({"detail": "Item added to cart"}, status=status.HTTP_201_CREATED)
        except MenuItem.DoesNotExist:
            return Response({"detail": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        Cart.objects.filter(user=request.user).delete()
        return Response({"detail": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_orders(request):
    if request.method == 'GET':
        orders = Order.objects.filter(user=request.user)
        order_data = [
            {
                'id': order.id,
                'delivery_crew': order.delivery_crew.username if order.delivery_crew else None,
                'status': order.status,
                'total': order.total,
                'date': order.date,
                'items': [
                    {
                        'menuitem': item.menuitem.title,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'price': item.price,
                    }
                    for item in OrderItem.objects.filter(order=order)
                ]
            }
            for order in orders
        ]
        return Response(order_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"detail": "No items in the cart"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total=0)
        total = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.quantity * item.unit_price,
            )
            total += item.quantity * item.unit_price
        order.total = total
        order.save()
        cart_items.delete()
        return Response({"detail": "Order created"}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'GET':
        if order.user != request.user:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        items = OrderItem.objects.filter(order=order)
        data = {
            'id': order.id,
            'delivery_crew': order.delivery_crew.username if order.delivery_crew else None,
            'status': order.status,
            'total': order.total,
            'date': order.date,
            'items': [
                {
                    'menuitem': item.menuitem.title,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'price': item.price,
                }
                for item in items
            ]
        }
        return Response(data, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH']:
        if not request.user.groups.filter(name='managers').exists():
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        delivery_crew_id = request.data.get('delivery_crew_id')
        status = request.data.get('status')
        if delivery_crew_id:
            delivery_crew = get_object_or_404(User, id=delivery_crew_id)
            order.delivery_crew = delivery_crew
        if status is not None:
            order.status = status
        order.save()
        return Response({"detail": "Order updated"}, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if not request.user.groups.filter(name='managers').exists():
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        order.delete()
        return Response({"detail": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_orders(request):
    if not request.user.groups.filter(name='managers').exists():
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    orders = Order.objects.all()
    order_data = [
        {
            'id': order.id,
            'user': order.user.username,
            'delivery_crew': order.delivery_crew.username if order.delivery_crew else None,
            'status': order.status,
            'total': order.total,
            'date': order.date,
            'items': [
                {
                    'menuitem': item.menuitem.title,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'price': item.price,
                }
                for item in OrderItem.objects.filter(order=order)
            ]
        }
        for order in orders
    ]
    return Response(order_data, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def delivery_crew_orders(request, order_id=None):
    if not request.user.groups.filter(name='deliver_crew').exists():
        return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        orders = Order.objects.filter(delivery_crew=request.user)
        order_data = [
            {
                'id': order.id,
                'user': order.user.username,
                'status': order.status,
                'total': order.total,
                'date': order.date,
                'items': [
                    {
                        'menuitem': item.menuitem.title,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'price': item.price,
                    }
                    for item in OrderItem.objects.filter(order=order)
                ]
            }
            for order in orders
        ]
        return Response(order_data, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        order = get_object_or_404(Order, id=order_id, delivery_crew=request.user)
        status = request.data.get('status')
        if status is not None:
            order.status = status
        order.save()
        return Response({"detail": "Order status updated"}, status=status.HTTP_200_OK)