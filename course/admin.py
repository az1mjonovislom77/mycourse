from django.contrib import admin
from django.db import models
from .models import Course, Teachers, Category, Module, Lesson, CourseView, Comment



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'students_count', 'rating', 'num_reviews', 'price', 'duration', 'lesson_count', 'module_count')
    search_fields = ('title', 'category__name')
    ordering = ('-rating',)
    prepopulated_fields = {'slug': ('title',)}

    readonly_fields = ('duration', 'lesson_count', 'module_count', 'students_count') 

    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'category', 'image', 'price',
                'rating', 'num_reviews', 'students_count',
                'duration', 'lesson_count', 'module_count',
                'description',
            )
        }),
    )


@admin.register(Teachers)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    search_fields = ('name', 'position')



class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    readonly_fields = ('duration', 'lesson_count', 'module_count', 'students_count')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CourseInline]
    search_fields = ('name',)



class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    readonly_fields = ('duration',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    inlines = [LessonInline]



@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'duration')
    readonly_fields = ('duration',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        course = obj.module.course

        total_duration = sum(
            (lesson.duration for module in course.modules.all() for lesson in module.lessons.all() if lesson.duration),
            models.DurationField().to_python("0:0:0")
        )

        lesson_count = sum(module.lessons.count() for module in course.modules.all())
        module_count = course.modules.count()

        course.duration = total_duration
        course.lesson_count = lesson_count
        course.module_count = module_count
        course.save(update_fields=['duration', 'lesson_count', 'module_count', 'students_count'])


@admin.register(CourseView)
class CourseViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__username', 'course__title')
    ordering = ('-viewed_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'course__title', 'text')