from django.contrib import admin
from .models import Category, Comments, Genre, Review, Title 


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    list_filter = ('year', 'category')
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date', 'title')
    search_fields = ('text', 'author__username', 'title__name')
    readonly_fields = ('pub_date',)
    ordering = ('-pub_date',)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date', 'review')
    search_fields = ('text', 'author__username', 'review__text')
    readonly_fields = ('pub_date',)
    ordering = ('-pub_date',)
