from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import validate_year
from api.constants import (
    CHARFIELD_MAX_LENGTH,
    SCORE_MIN_VALUE,
    SCORE_MAX_VALUE,
    SLUGFIELD_MAX_LENGTH,
    STR_SLICE_LENGTH,
)


User = get_user_model()


class CategoryAndGenreBaseModel(models.Model):
    """
    Базовая модель для категорий и жанров.
    """

    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUGFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_SLICE_LENGTH]


class Category(CategoryAndGenreBaseModel):
    """
    Модель категорий произведений.
    """

    class Meta(CategoryAndGenreBaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryAndGenreBaseModel):
    """
    Модель жанров.
    """

    class Meta(CategoryAndGenreBaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """
    Модель произведений.
    """

    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        db_index=True,
        validators=(validate_year,)
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


class ReviewCommentBaseModel(models.Model):
    """
    Базовая модель для отзывов и комментариев.
    """

    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.text[:STR_SLICE_LENGTH]


class Review(ReviewCommentBaseModel):
    """
    Модель отзывов на произведения.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(SCORE_MIN_VALUE),
                    MaxValueValidator(SCORE_MAX_VALUE)),
        verbose_name='Оценка'
    )

    class Meta(ReviewCommentBaseModel.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_per_author_title'
            ),
        )
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comments(ReviewCommentBaseModel):
    """
    Модель комментариев.
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(ReviewCommentBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
