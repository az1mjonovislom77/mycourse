from django.db import models
from datetime import timedelta
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

    def get_duration_parts(self):
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return {'hours': hours, 'minutes': minutes}

    def __str__(self):
        return self.title


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


class Lesson(models.Model):
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='videos/')
    duration = models.DurationField(blank=True, null=True)

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

        course = self.module.course
        course.lesson_count = sum(
            module.lessons.count() for module in course.modules.all()
        )

        course.module_count = course.modules.count()
        total_duration = timedelta()
        for module in course.modules.all():
            for lesson in module.lessons.all():
                if lesson.duration:
                    total_duration += lesson.duration

        course.duration = total_duration
        course.save(update_fields=['duration', 'lesson_count', 'module_count'])

    def __str__(self):
        return self.title
