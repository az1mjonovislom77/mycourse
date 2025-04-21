from django.db import models
from datetime import timedelta
from django.conf import settings
from moviepy.editor import VideoFileClip


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    students = models.PositiveIntegerField(default=0)
    duration = models.DurationField(default=timedelta())
    description = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    num_reviews = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses', default=1)
    slug = models.SlugField(unique=True, null=True, blank=True)
    lesson_count = models.PositiveIntegerField(default=0)
    module_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def students_count(self):
        return self.courseview_set.count()

    def get_duration_parts(self):
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return {'hours': hours, 'minutes': minutes}

    def update_course_info(self):
        self.lesson_count = sum(module.lessons.count() for module in self.modules.all())
        self.module_count = self.modules.count()

        total_duration = timedelta()
        for module in self.modules.all():
            for lesson in module.lessons.all():
                if lesson.duration:
                    total_duration += lesson.duration

        self.duration = total_duration
        self.save(update_fields=['duration', 'lesson_count', 'module_count'])


class Teachers(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='teachers/', blank=True, null=True)

    def __str__(self):
        return self.name


class Module(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        course.update_course_info()


class Lesson(models.Model):
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='videos/')
    duration = models.DurationField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.video:
            try:
                clip = VideoFileClip(self.video.path)
                self.duration = timedelta(seconds=int(clip.duration))

                clip.reader.close()
                if clip.audio:
                    clip.audio.reader.close_proc()

                super().save(update_fields=['duration'])

            except Exception as e:
                print(f"Xatolik video duration olishda: {e}")

        self.module.course.update_course_info()

    def delete(self, *args, **kwargs):
        course = self.module.course
        super().delete(*args, **kwargs)
        course.update_course_info()


class CourseView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} viewed {self.course}"


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.rating}⭐"
