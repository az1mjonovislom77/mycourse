from random import randint
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.core.mail import EmailMessage
from django.conf import settings
from users.models import CustomUser
from .forms import CustomUserCreationForm

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
