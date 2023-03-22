from django.urls import path

from user import views

app_name = 'user'
urlpatterns = [
    path('create/', views.UserAPIView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('', views.UserListAPIView.as_view(), name='user_list'),
]
