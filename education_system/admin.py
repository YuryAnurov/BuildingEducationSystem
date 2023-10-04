from django.contrib import admin
from .models import Product, Lesson, LessonView


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner')
    filter_horizontal = ['students']


class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'display_products')

    def display_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()])

    display_products.short_description = 'Products'
    filter_horizontal = ['products']


class LessonViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'watched_time_seconds', 'is_watched')
    exclude = ('is_watched', 'last_watched_at')


admin.site.register(Product, ProductAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonView, LessonViewAdmin)
