# models.py
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Case, When, Value, F, IntegerField


class Product(models.Model):
    # В задании упомянуты понятия "владелец" и "имеющий доступ". На всякий случай, помимо сущности "имеющий
    # доступ" students, добавил еще сущность owner, хоть далее в задании это свойство и не используется.
    # В заполненной бд я внес владельцев в 'студенты' своих продуктов, чтобы с их аккаунтом была видна
    # информация по их продукту в API 'уроки по продукту'
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products_owned')
    students = models.ManyToManyField(User, related_name='products_enrolled')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    video_link = models.URLField()
    duration_seconds = models.IntegerField()
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f'{self.title}'


class LessonView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    watched_time_seconds = models.IntegerField(default=0)
    is_watched = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        has_access = self.lesson.products.filter(students=self.student).exists()
        if has_access:
            duration = self.lesson.duration_seconds
            # здесь ограничиваем время просмотра за один раз:
            if self.watched_time_seconds > duration:
                self.watched_time_seconds = duration
            elif self.watched_time_seconds < 0:
                self.watched_time_seconds = 0
            if duration > 0 and self.watched_time_seconds > 0:
                existing_record = LessonView.objects.filter(student=self.student, lesson=self.lesson,).first()
                if existing_record:
                    LessonView.objects.filter(id=existing_record.id).update(
                        # но здесь допускаем, что суммарное время просмотра может быть больше длительности:
                        watched_time_seconds=F('watched_time_seconds') + self.watched_time_seconds,
                        is_watched=Case(
                            When(watched_time_seconds__gte=Value(0.8 * duration), then=Value(True)),
                            default=Value(False),
                            output_field=IntegerField()
                        ),
                        last_watched_at=timezone.now()
                    )

                else:
                    self.is_watched = (self.watched_time_seconds / duration) * 100 >= 80
                    self.last_watched_at = timezone.now()
                    super().save(*args, **kwargs)
        else:
            raise ValueError("Студент не имеет доступа к этому уроку.")

    def __str__(self):
        return f'{self.student.username} - {self.lesson.title}'
