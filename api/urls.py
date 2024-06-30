from django.urls import path, re_path
from . import views

# namespace
app_name = 'api'

urlpatterns = [
    path('login', views.LoginView.as_view(), name='api-login'),
    path('user/<int:user_id>', views.UserInfoView.as_view(), name='api-user-info'),
    path('menus/routes', views.MenuRoutesView.as_view(), name='api-menu-routes'),
]
