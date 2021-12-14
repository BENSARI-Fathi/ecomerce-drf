from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (Product, Order,
                     OrderItem, ShippingAddress,
                     Review)
from django.contrib.auth.models import User


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['user']

    def get_reviews(self, obj):
        reviews = obj.review_set.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.price = validated_data['price']
        instance.brand = validated_data['brand']
        instance.category = validated_data['category']
        instance.countInStock = validated_data['countInStock']
        instance.description = validated_data['description']
        instance.save()
        return instance

    def create(self, validated_data):
        new_product = Product.objects.create(
            user=self.context['request'].user,
            name='Sample Name',
            price=0,
            brand='Sample Brand',
            countInStock=0,
            category='Sample Category',
            description=''
        )
        return new_product


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            '_id',
            'username',
            'email',
            'name',
            'isAdmin',
        ]

    def get__id(self, obj):
        return obj.id

    def get_name(self, obj):
        return obj.first_name if obj.first_name != '' else obj.email

    def get_isAdmin(self, obj):
        return obj.is_staff

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)
        if qs.exists():
            raise serializers.ValidationError('User with this email already exist !')
        return value


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['name'] = user.username

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializer(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    orderItems = serializers.SerializerMethodField(read_only=True)
    shippingAddress = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_orderItems(self, obj):
        items = obj.orderitem_set.all()
        serializer = OrderItemSerializer(items, many=True, context=self.context)
        return serializer.data

    def get_shippingAddress(self, obj):
        address = obj.shippingaddress
        serializer = ShippingAddressSerializer(address, many=False)
        return serializer.data

    def get_user(self, obj):
        try:
            return {"name": obj.user.first_name, "email": obj.user.email}
        except:
            return {"name": "Unknown", "email": "Unknown"}

    def update(self, instance, validated_data):
        instance.isPaid = True
        instance.paidAt = timezone.now()
        instance.save()
        return instance


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image')

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(obj.image)
