from random import randint
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.views import View
from django.views.generic import CreateView, TemplateView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from .forms import CustomUserCreationForm
from .serializers import RegisterSerializer, LoginSerializer, VerifyEmailSerializer
from .permissions import IsAuthenticated, IsActiveUser
from django.urls import reverse_lazy

User = get_user_model()


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Tizimga muvaffaqiyatli kirdingiz!")
                return redirect("course:index")
            else:
                messages.error(request, "Sizning emailingiz tasdiqlanmagan")
                return redirect('users:login_page')
        else:
            messages.error(request, "Email yoki parol noto‘g‘ri!")
    return render(request, 'users/login.html')


def logout_page(request):
    logout(request)
    return redirect("course:index")


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            verification_code = user.verification_code
            mail_subject = 'Your Registration Verification Code'
            message = f'Hello {user.email},\n\nYour verification code is: {verification_code}'

            email = EmailMessage(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.send()

            return Response({'message': 'User registered successfully. Check your email for verification.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'access': access_token,
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = serializer.validated_data['verification_code']
            try:
                user = CustomUser.objects.get(verification_code=verification_code)
                user.is_active = True
                user.verification_code = ''
                user.save()

                return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'message': 'Invalid verification code!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:email_page')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.verification_code = self.generate_verification_code()
        user.save()

        verification_code = user.verification_code
        mail_subject = 'Your Registration Verification Code'
        message = f'Hello {user.email},\n\nYour verification code is: {verification_code}'

        email = EmailMessage(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.send()

        return redirect(self.success_url)

    def generate_verification_code(self):
        return str(randint(100000, 999999))


class EmailPageView(TemplateView):
    template_name = 'users/email_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            context['user'] = user
            context['verification_code'] = user.verification_code
        return context


class VerifyEmailView(View):
    def post(self, request):
        verification_code = request.POST.get('verification_code')

        try:
            user = CustomUser.objects.get(verification_code=verification_code)
            user.is_active = True
            user.verification_code = ''
            user.save()
            login(request, user)

            messages.success(request, "Your email has been successfully verified!")
            return redirect('course:index')

        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid verification code!")
            return redirect('users:email_page')
