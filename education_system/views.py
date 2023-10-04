from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Lesson, Product
from .serializers import LessonsAllSerializer, LessonPerProductSerializer, ProductDetailSerializer


class HomeView(APIView):
    def get(self, request):
        django_admin_url = request.build_absolute_uri(reverse('admin:login'))
        lesson_list_url = request.build_absolute_uri(reverse('lesson-list'))
        product_lesson_list_url = request.build_absolute_uri(reverse('product-lesson-list', args=[1]))
        product_statistics_url = request.build_absolute_uri(reverse('product-statistics'))

        data = {
            'API1 - lesson_list_url': lesson_list_url,
            'API2 - product_lesson_list_url': product_lesson_list_url,
            'API3 - product_statistics_url': product_statistics_url,
            'Sign in': django_admin_url,
        }

        return Response(data, status=status.HTTP_200_OK)


class LessonListView(generics.ListAPIView):
    serializer_class = LessonsAllSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        student = get_object_or_404(User, id=user.id)
        lessons = Lesson.objects.filter(products__students=student)
        return lessons


class ProductLessonListView(generics.ListAPIView):
    serializer_class = LessonPerProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id, students=user)
        product_lessons = Lesson.objects.filter(products=product)
        return product_lessons


class ProductStatisticsView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
