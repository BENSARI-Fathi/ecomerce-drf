from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, mixins, permissions
from .serializers import (ProductSerializer,
                          MyTokenObtainPairSerializer,
                          UserSerializer, OrderSerializer)
from .models import (Product, Order,
                     ShippingAddress, OrderItem,
                     Review)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .permissions import NotAuthenticated, IsStaffOrOwner, IsAdminOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def get_route(request):
    dico = {
        "name": "Fathi",
        "last_name": "BENSARI",
    }
    return Response(dico)


class GetUserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class UpdateUserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data
        user.first_name = data['name']
        user.email = data['email']
        if data['password'] != '':
            is_true = user.check_password(data['oldPassword'])
            if is_true:
                user.set_password(data['password'])
            else:
                return Response(data='Old Password is incorrect !', status=HTTP_400_BAD_REQUEST)
        user.save()
        refresh = RefreshToken.for_user(user)
        resp = UserSerializer(user, many=False).data
        resp['access'] = str(refresh.access_token)
        resp['refresh'] = str(refresh)
        return Response(resp)


class RegisterUser(APIView):
    permission_classes = [NotAuthenticated]

    def post(self, request):
        data = request.data
        UserSerializer().validate_email(data['email'])
        user = User(first_name=data['name'],
                    email=data['email'],
                    username=data['email'])
        user.set_password(data['password'])
        user.save()
        refresh = RefreshToken.for_user(user)
        resp = UserSerializer(user, many=False).data
        resp['access'] = str(refresh.access_token)
        resp['refresh'] = str(refresh)
        return Response(resp)


class GetUsers(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    # authentication_classes = [SessionAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProductListApiView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = [IsAdminOrReadOnly]
    # authentication_classes = [SessionAuthentication]
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        qs = Product.objects.all().order_by('-created_at')
        query = self.request.query_params.get('q')
        if query is not None:
            qs = qs.filter(name__icontains=query)
        page = self.request.query_params.get('page')
        paginator = Paginator(qs, 5)
        try:
            qs = paginator.page(page)
        except PageNotAnInteger:
            qs = paginator.page(1)
        except EmptyPage:
            qs = paginator.page(paginator.num_pages)
        if page is None:
            page = 1

        resp = ProductSerializer(qs, many=True, context={'request': request})
        return Response({'products': resp.data, 'page': int(page), 'pages': paginator.num_pages})

    # def get_queryset(self):
    #     qs = Product.objects.all().order_by('-created_at')
    #     query = self.request.query_params.get('q')
    #     if query is not None:
    #         qs = qs.filter(name__icontains=query)
    #     page = self.request.query_params.get('page')
    #     paginator = Paginator(qs, 2)
    #     try:
    #         qs = paginator.page(page)
    #     except PageNotAnInteger:
    #         qs = paginator.page(1)
    #     except EmptyPage:
    #         qs = paginator.page(paginator.num_pages)
    #     return qs

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


class ProductDetailApiView(mixins.DestroyModelMixin, mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [IsAdminOrReadOnly]
    # authentication_classes = []
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GetTopProducts(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = Product.objects.filter(rating__gte=3.5).order_by('-rating')[:5]
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class AddOrderItems(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        order_items = data['orderItems']
        shipping_address = data['shippingAddress']
        if len(order_items) == 0:
            return Response({'detail': 'No Order Items'}, status=HTTP_400_BAD_REQUEST)
        # create order

        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice=data['taxPrice'],
            shippingPrice=data['shippingPrice'],
            totalPrice=data['totalPrice']
        )

        # create shippingAddress
        shipping = ShippingAddress.objects.create(
            order=order,
            address=shipping_address['address'],
            city=shipping_address['city'],
            postalCode=shipping_address['postalCode'],
            country=shipping_address['country']
        )
        # create orderItems for each product
        for prod in order_items:
            product = Product.objects.get(_id=prod['product'])
            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                qty=prod['qty'],
                price=prod['price'],
                image=product.image.url,
            )
            # update the stock count
            product.countInStock -= item.qty
            product.save()
        resp = OrderSerializer(order, many=False, context={'request': self.request}).data
        resp['user'] = user.username
        return Response(resp)


class OrderListApiView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.select_related('user').all()
    serializer_class = OrderSerializer


class OrderDetailApiView(mixins.DestroyModelMixin, mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = [IsStaffOrOwner]
    # authentication_classes = []
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateOrderToDelivered(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, **kwargs):
        pk = kwargs['pk']
        order = Order.objects.get(_id=pk)
        order.isDelivered = True
        order.deliveredAt = timezone.now()
        order.save()
        serializer = OrderSerializer(order, many=False, context={'request': request})
        return Response(serializer.data)


class CustomerOrdersApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = user.order_set.all()
        resp = OrderSerializer(orders, many=True, context={'request': request})
        return Response(resp.data)


class DeleteUser(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = kwargs['pk']
        customer = User.objects.get(pk=pk)
        customer.delete()
        return Response('Deleted successfully !')


class GetUserByID(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, **kwargs):
        pk = kwargs['pk']
        customer = User.objects.get(pk=pk)
        serializer = UserSerializer(customer, many=False)
        return Response(serializer.data)

    def put(self, request, **kwargs):
        pk = kwargs['pk']
        customer = User.objects.get(pk=pk)
        data = request.data
        customer.first_name = data['name']
        customer.email = data['email']
        customer.is_staff = data['isAdmin']
        customer.save()
        resp = UserSerializer(customer, many=False).data
        return Response(resp)


class UploadImageView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        data = request.data
        product_id = data['product_id']
        product = Product.objects.get(_id=product_id)
        product.image = request.FILES.get('image')
        product.save()
        return Response('image was successfully uploaded')


class CreateReviewToProduct(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, **kwargs):
        pk = kwargs['pk']
        user = request.user
        product = Product.objects.get(_id=pk)
        data = request.data

        # Review already exist
        already_exist = product.review_set.filter(user=user).exists()
        if already_exist:
            resp = {'detail': 'Product already reviewed'}
            return Response(resp, status=HTTP_400_BAD_REQUEST)
        # Rating is None or Zero
        elif data['rating'] == 0:
            resp = {'detail': 'Product must have a rating'}
            return Response(resp, status=HTTP_400_BAD_REQUEST)
        # Create the Review
        else:
            review = Review.objects.create(
                user=user,
                product=product,
                name=user.first_name,
                rating=data['rating'],
                comment=data['comment']
            )
            reviews = product.review_set.all()
            product.numReviews = len(reviews)
            total = 0
            for rev in reviews:
                total += rev.rating
            product.rating = total / len(reviews)
            product.save()
        resp = ProductSerializer(product, many=False, context={'request': request})
        return Response(resp.data)

# superuser name : mine ; pw : ouedknissclone
# custom user => name:faiza@email.com; pw : bensari1996
