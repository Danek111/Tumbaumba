from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from .permissions import IsAuthenticatedAndNotAdmin
from rest_framework.response import Response
from . import serializers
from rest_framework.authtoken.models import Token
from .models import User, Product, Cart, Order


@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    serializer = serializers.RegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": {
                "code": 422,
                "message": "Нарушение правил валидации",
                "errors":
                    serializer.errors
            }
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    user = serializer.save()
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        "data": {
            "user_token": token.key
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = serializers.LoginSerializer(data=request.data,
                                             context={'request': request})
    if not serializer.is_valid():
        return Response({
            "error": {
                "code": 422,
                "message": "Нарушение правил валидации",
                "errors":
                    serializer.errors
            }
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        user = User.objects.get(email=serializer.validated_data['email'])
        if not user.check_password(serializer.validated_data['password']):
            return Response({
                "error": {
                    "code": 401,
                    "message": "Authentication failed"
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({
            "error": {
                "code": 401,
                "message": "Authentication failed"
            }
        }, status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        "data": {
            "user_token": token.key
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNotAdmin])
def logout(request):
    request.user.auth_token.delete()
    return Response({"data": {"message": "logout"}}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    products = Product.objects.all()
    serializer = serializers.ProductSerializer(products, many=True)
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndNotAdmin])
def get_cart(request):
    carts = Cart.objects.filter(user=request.user)
    for cart in carts:
        response = {"data": []}
        for index, product in enumerate(cart.products.all()):
            response["data"].append({
                "id": index + 1,
                "product_id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price
            })
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def get_create_order(request):
    if request.method == 'GET':
        order = Order.objects.filter(user=request.user)
        serializer = serializers.OrderSerializer(order, many=True)
        return Response({
            "data": {
                serializer.data
            }
        }, status=status.HTTP_200_OK)
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": {
                "code": 422,
                "message": "Cart is empty"
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not cart:
            return Response({"error": {
                "code": 422,
                "message": "Cart is empty"
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        order = Order.objects.create(user=request.user)
        total = 0
        for product in cart.products.all():
            total += product.price
            order.products.add(product)
        order.order_price = total
        order.save()
        cart.delete()
        return Response(
            {
                "data": {
                    "order_id": order.id,
                    "message": "Order is processed"
                }
            }, status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticatedAndNotAdmin])
def add_delete_to_cart(request, pk):
    if request.method == "POST":
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({
                "error": {
                    "code": 404,
                    "message": "Not found"
                }
            }, status=status.HTTP_404_NOT_FOUND)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
        serializer = serializers.CartSerializer(cart)
        return Response({
            "data": {
                "message": "Product add to cart"
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        cart = Cart.objects.get(user=request.user)
        try:
            product = cart.products.all()[pk - 1]
        except:
            return Response({
                "error": {
                    "code": 404,
                    "message": "Not found"
                }
            }, status=status.HTTP_404_NOT_FOUND)

        cart.products.remove(product)
        return Response({
            "data": {
                "message": "Item removed from cart"
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product(request):
    serializer = serializers.ProductSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": {
                "code": 422,
                "message": "Нарушение правил валидации",
                "errors":
                    serializer.errors
            }
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    serializer.save()
    return Response({
        "data": {
            "id": serializer.data['id'],
            "message": "Product added"
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def edit_delete_product(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({
            "error": {
                "code": 404,
                "message": "Not found"
            }
        }, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = serializers.ProductSerializer(product)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    if request.method == 'PATCH':
        serializer = serializers.ProductSerializer(instance=product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "error": {
                    "code": 422,
                    "message": "Нарушение правил валидации",
                    "errors":
                        serializer.errors
                }
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        serializer.save()
        return Response({
            "body": serializer.data
        }, status=status.HTTP_200_OK)
    if request.method == 'DELETE':
        product.delete()
        return Response({
            "body": {
                "message": "Product removed"
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = serializers.RegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": {
                "code": 422,
                "message": "Нарушение правил валидации",
                "errors": serializer.errors
            }
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    user = serializer.save()
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        "data": {
            "user_token": token.key
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = serializers.LoginSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response({
            "error": {
                "code": 422,
                "message": "Нарушение правил валидации",
                "errors": serializer.errors
            }
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        user = User.objects.get(serializer.validated_data['email'])
        if not user.check_password(serializer.validated_data['password']):
            return Response({
                "error": {
                    "code": 401,
                    "message": "Authentication failed"
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({
            "error": {
                "code": 401,
                "message": "Authentication failed"
            }
        }, status=status.HTTP_401_UNAUTHORIZED)
    token, created = Token.objects.get_or_create(user=user)
            return Response({
            "data": {
                "user_token" : token.key
            }
            },status=status.HTTP_200_OK)