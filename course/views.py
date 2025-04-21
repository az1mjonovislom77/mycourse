from django.views.generic import TemplateView, ListView, DetailView
from .models import Course, Teachers, Category, Lesson, CourseView, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import CommentForm
from django.db.models import Avg


class IndexView(TemplateView):
    template_name = 'course/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = (
            Course.objects
            .annotate(average_rating=Avg('comments__rating'))
            .order_by('-average_rating')[:6]
        )
        context['teachers'] = Teachers.objects.all()
        context['categories'] = Category.objects.all()
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'course/category_list.html'
    context_object_name = 'categories'


from django.db.models import Avg

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'course/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        courses_with_ratings = category.courses.annotate(average_rating=Avg('comments__rating'))

        context['courses'] = courses_with_ratings
        return context



class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

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
    login_url = 'users/login.html'

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

    def get_object(self):
        obj = super().get_object()
        obj.update_course_info()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.prefetch_related('lessons')
        lesson_id = self.request.GET.get('lesson')
        if lesson_id:
            context['selected_lesson'] = Lesson.objects.get(id=lesson_id)
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