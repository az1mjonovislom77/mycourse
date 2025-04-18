from django.contrib import admin
from django.db import models
from .models import Course, Teachers, Category, Module, Lesson



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'students', 'rating', 'num_reviews', 'price', 'duration', 'lesson_count', 'module_count')
    list_filter = ('category', 'rating', 'students')
    search_fields = ('title', 'category__name')
    ordering = ('-rating',)
    prepopulated_fields = {'slug': ('title',)}

    readonly_fields = ('duration', 'lesson_count', 'module_count')  # faqat o‘qish uchun

    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'category', 'image', 'price',
                'rating', 'num_reviews', 'students',
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
    readonly_fields = ('duration', 'lesson_count', 'module_count')


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
        """Yangi Lesson saqlanganda Course.duration, lesson_count va module_count ni yangilaymiz."""
        super().save_model(request, obj, form, change)

        course = obj.module.course

        # Duration hisoblash
        total_duration = sum(
            (lesson.duration for module in course.modules.all() for lesson in module.lessons.all() if lesson.duration),
            models.DurationField().to_python("0:0:0")
        )

        lesson_count = sum(module.lessons.count() for module in course.modules.all())
        module_count = course.modules.count()

        course.duration = total_duration
        course.lesson_count = lesson_count
        course.module_count = module_count
        course.save(update_fields=['duration', 'lesson_count', 'module_count'])
