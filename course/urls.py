from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    IndexView, CategoryListView, CategoryDetailView,
    CourseDetailView, BuyCourseView, CourseVideoView,
    CourseListView, AboutView,
    
    # API views
    CategoryListCreateAPIView, CategoryRetrieveUpdateDestroyAPIView,
    CourseListCreateAPIView, CourseRetrieveUpdateDestroyAPIView,
    TeacherListCreateAPIView,
    ModuleListCreateAPIView, LessonListCreateAPIView,
    CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView
)

app_name = 'course'

urlpatterns = [
    # Template views
    path('', IndexView.as_view(), name='index'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('course/<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('buy/<slug:slug>/', BuyCourseView.as_view(), name='buy_course'),
    path('course/<slug:slug>/video/', CourseVideoView.as_view(), name='course_video'),
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('about/', AboutView.as_view(), name='about'),

    # JWT auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Category API
    path('api/categories/', CategoryListCreateAPIView.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    # Course API
    path('api/courses/', CourseListCreateAPIView.as_view(), name='course-list'),
    path('api/courses/<int:pk>/', CourseRetrieveUpdateDestroyAPIView.as_view(), name='course-detail'),

    # Teacher API
    path('api/teachers/', TeacherListCreateAPIView.as_view(), name='teacher-list'),

    # Module and Lesson API
    path('api/modules/', ModuleListCreateAPIView.as_view(), name='module-list'),
    path('api/lessons/', LessonListCreateAPIView.as_view(), name='lesson-list'),

    # Comment API
    path('api/comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('api/comments/<int:pk>/', CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
