from django.urls import path
from .views import (get_route, ProductListApiView,
                    ProductDetailApiView, MyTokenObtainPairView,
                    UpdateUserProfile, GetUsers,
                    RegisterUser, AddOrderItems,
                    OrderDetailApiView, CustomerOrdersApiView,
                    DeleteUser, GetUserByID,
                    UploadImageView, OrderListApiView,
                    UpdateOrderToDelivered, CreateReviewToProduct,
                    GetTopProducts)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', get_route),
    path('user/update/', UpdateUserProfile.as_view()),
    path('user/register/', RegisterUser.as_view()),
    path('user/order/', CustomerOrdersApiView.as_view()),
    path('user/<int:pk>/delete/', DeleteUser.as_view()),
    path('user/<int:pk>/', GetUserByID.as_view()),
    path('users/', GetUsers.as_view()),

    path('products/', ProductListApiView.as_view()),
    path('products/top/', GetTopProducts.as_view()),
    path('product/<int:pk>', ProductDetailApiView.as_view()),
    path('product/<int:pk>/review/', CreateReviewToProduct.as_view()),
    path('product/upload/', UploadImageView.as_view()),

    path('orders/', OrderListApiView.as_view()),
    path('order/add', AddOrderItems.as_view()),
    path('order/<int:pk>', OrderDetailApiView.as_view()),
    path('order/<int:pk>/deliver/', UpdateOrderToDelivered.as_view()),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
