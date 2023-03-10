from django.urls import path

from user import views

app_name = 'user'
urlpatterns = [
    path('create/', views.UserAPIView.as_view(), name='create'),
]
