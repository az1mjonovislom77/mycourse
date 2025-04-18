from django.urls import path
from .views import IndexView, CategoryListView, CategoryDetailView, CourseDetailView, BuyCourseView, CourseVideoView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'course'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('course_detail/<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('buy/<slug:slug>/', BuyCourseView.as_view(), name='buy_course'),
    path('course/<slug:slug>/video/', CourseVideoView.as_view(), name='course_video'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
