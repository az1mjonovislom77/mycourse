from django.urls import path
from django.views.generic import TemplateView

from users import views
from users.views import RegisterView, VerifyEmailView, RegisterAPIView, LoginAPIView, VerifyEmailAPIView, LogoutAPIView

app_name = 'users'

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_page, name='logout_page'),
    path('register/', RegisterView.as_view(), name='register_page'),
    path('email_page/', TemplateView.as_view(template_name='users/email_page.html'), name='email_page'),
    path('verify/', VerifyEmailView.as_view(), name='verify_email'),
    
    #Api 
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
]

