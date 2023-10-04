from django.urls import path
from .views import LessonListView, ProductLessonListView, ProductStatisticsView

urlpatterns = [
    path('lessons/', LessonListView.as_view(), name='lesson-list'),
    path('products/<int:product_id>/lessons/', ProductLessonListView.as_view(), name='product-lesson-list'),
    path('products/statistics/', ProductStatisticsView.as_view(), name='product-statistics'),
]
