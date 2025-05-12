from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Course, Teachers, Category, Lesson, CourseView, Comment, Module
from .forms import CommentForm
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    TeacherSerializer,
    ModuleSerializer,
    LessonSerializer,
    CourseViewSerializer,
    CommentSerializer,
    MyTokenObtainPairSerializer
)

# JWT Token views
token_obtain_pair = TokenObtainPairView.as_view(serializer_class=MyTokenObtainPairSerializer)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Template-based Views


class IndexView(TemplateView):
    template_name = 'course/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.annotate(average_rating=Avg('comments__rating')).order_by('-average_rating')[:6]
        context['teachers'] = Teachers.objects.all()
        context['categories'] = Category.objects.all()
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'course/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'course/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['courses'] = category.courses.annotate(average_rating=Avg('comments__rating'))
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = '/users/login/'

    def get_object(self):
        obj = super().get_object()
        obj.update_course_info()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context['duration_parts'] = course.get_duration_parts()
        context['form'] = CommentForm()
        context['comments'] = course.comments.select_related('user').order_by('-created_at')
        average_rating = course.comments.aggregate(Avg('rating'))['rating__avg'] or 0
        context['average_rating'] = round(average_rating, 1)
        context['num_reviews'] = course.comments.count()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.course = self.object
            comment.user = request.user
            comment.save()
        return redirect('course:course_detail', slug=self.object.slug)


class BuyCourseView(LoginRequiredMixin, View):
    login_url = '/users/login/'

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        if not CourseView.objects.filter(user=request.user, course=course).exists():
            CourseView.objects.create(user=request.user, course=course)
        messages.success(request, f"{course.title} kursi muvaffaqiyatli sotib olindi!")
        return redirect('course:course_video', slug=course.slug)


class CourseVideoView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'course/course_video.html'
    context_object_name = 'course'
    login_url = '/users/login/'

    def get_object(self):
        obj = super().get_object()
        obj.update_course_info()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.prefetch_related('lessons')
        lesson_id = self.request.GET.get('lesson')
        if lesson_id:
            context['selected_lesson'] = get_object_or_404(Lesson, id=lesson_id)
        return context


class CourseListView(ListView):
    model = Course
    template_name = 'course/course.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.annotate(average_rating=Avg('comments__rating'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class AboutView(ListView):
    model = Course
    template_name = 'course/about.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.annotate(average_rating=Avg('comments__rating'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# API Views


# DRY Base Classes
class BaseListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BaseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Category API
class CategoryListCreateAPIView(BaseListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Course API
class CourseListCreateAPIView(BaseListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# Teachers API
class TeacherListCreateAPIView(BaseListCreateAPIView):
    queryset = Teachers.objects.all()
    serializer_class = TeacherSerializer

class TeacherRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset = Teachers.objects.all()
    serializer_class = TeacherSerializer

# Module API
class ModuleListCreateAPIView(BaseListCreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class ModuleRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

# Lesson API
class LessonListCreateAPIView(BaseListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

# CourseView API
class CourseViewListCreateAPIView(BaseListCreateAPIView):
    queryset = CourseView.objects.all()
    serializer_class = CourseViewSerializer
    permission_classes = [permissions.IsAuthenticated]

# Comment API
class CommentListCreateAPIView(BaseListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentRetrieveUpdateDestroyAPIView(BaseRetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
