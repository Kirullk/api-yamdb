import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

from api.constants import (
    CHARFIELD_NAME_MAX_LENGTH,
    SCORE_MIN_VALUE,
    SCORE_MAX_VALUE,
    SLUGFIELD_MAX_LENGTH,
    STR_SLICE_LENGTH,
)


User = get_user_model()


def current_year():
    return datetime.date.today().year


class Category(models.Model):
    """
    Модель категорий произведений.
    """

    name = models.CharField(
        max_length=CHARFIELD_NAME_MAX_LENGTH,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=SLUGFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Модель жанров.
    """

    name = models.CharField(
        max_length=CHARFIELD_NAME_MAX_LENGTH,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=SLUGFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Модель произведений.
    """

    name = models.CharField(
        max_length=CHARFIELD_NAME_MAX_LENGTH,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(
                current_year,
                message='Год выпуска не может быть больше текущего!'
            )
        ]
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель отзывов на произведения.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(SCORE_MIN_VALUE),
                    MaxValueValidator(SCORE_MAX_VALUE)),
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_per_author_title'
            ),
        )
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:STR_SLICE_LENGTH,]


class Comments(models.Model):
    """
    Модель комментариев.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:STR_SLICE_LENGTH,]
