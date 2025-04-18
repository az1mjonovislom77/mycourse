from django.views.generic import TemplateView, ListView, DetailView
from .models import Course, Teachers, Category, Lesson
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


class IndexView(TemplateView):
    template_name = 'course/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
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
        context['courses'] = category.courses.all()
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context['duration_parts'] = course.get_duration_parts()
        return context

class BuyCourseView(LoginRequiredMixin, View):
    login_url = 'users/login.html' 

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)

        messages.success(request, f"{course.title} kursi muvaffaqiyatli sotib olindi!")
        return redirect('course:course_video', slug=course.slug)
    


class CourseVideoView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'course/course_video.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.prefetch_related('lessons')
        lesson_id = self.request.GET.get('lesson')
        if lesson_id:
            context['selected_lesson'] = Lesson.objects.get(id=lesson_id)
        return context