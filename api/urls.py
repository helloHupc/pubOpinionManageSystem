from django.urls import path, re_path
from . import views

# namespace
app_name = 'api'

urlpatterns = [
    path('login', views.LoginView.as_view(), name='api-login'),
    path('user/<int:user_id>', views.UserInfoView.as_view(), name='api-user-info'),
    path('menus/routes', views.MenuRoutesView.as_view(), name='api-menu-routes'),
    path('key_word/<str:action>', views.KeyWordView.as_view(), name='api-key-word-action'),
    path('crawler/<str:action>', views.CrawlerView.as_view(), name='api-crawler-action'),
    path('dashboard/<str:action>', views.DashboardView.as_view(), name='api-dashboard-action'),
]
