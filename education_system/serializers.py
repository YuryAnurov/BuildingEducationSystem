# serializers.py
from rest_framework import serializers
from .models import Lesson, LessonView, Product
from django.db.models import Sum
from django.contrib.auth.models import User


class LessonsAllSerializer(serializers.ModelSerializer):
    watched_time_seconds = serializers.SerializerMethodField()
    is_watched = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['title', 'video_link', 'duration_seconds', 'watched_time_seconds', 'is_watched']

    def get_watched_time_seconds(self, obj):
        user = self.context['request'].user
        lesson_view = LessonView.objects.filter(student=user, lesson=obj).first()
        return lesson_view.watched_time_seconds if lesson_view else 0

    def get_is_watched(self, obj):
        user = self.context['request'].user
        lesson_view = LessonView.objects.filter(student=user, lesson=obj).first()
        return lesson_view.is_watched if lesson_view else False


class LessonPerProductSerializer(LessonsAllSerializer):
    last_watched_at = serializers.SerializerMethodField()

    class Meta(LessonsAllSerializer.Meta):
        model = Lesson
        fields = LessonsAllSerializer.Meta.fields + ['last_watched_at']

    def get_last_watched_at(self, obj):
        user = self.context['request'].user
        lesson_view = LessonView.objects.filter(student=user, lesson=obj).first()
        if lesson_view:
            return lesson_view.last_watched_at.strftime("%Y-%m-%d, %H:%M")
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    watched_lessons_count = serializers.SerializerMethodField()
    total_watched_time = serializers.SerializerMethodField()
    unique_students_count = serializers.SerializerMethodField()
    acquisition_percent = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name',
                  'watched_lessons_count', 'total_watched_time',
                  'unique_students_count', 'acquisition_percent']

    def get_watched_lessons_count(self, obj):
        return LessonView.objects.filter(lesson__products=obj, is_watched=True).count()

    def get_total_watched_time(self, obj):
        return LessonView.objects.filter(
                lesson__products=obj).aggregate(Sum('watched_time_seconds'))['watched_time_seconds__sum']

    def get_unique_students_count(self, obj):
        return obj.students.count()

    def get_acquisition_percent(self, obj):
        total_users_count = User.objects.all().count()
        access_count = obj.students.count()
        percent = (access_count / total_users_count) * 100
        return round(percent, 2)
