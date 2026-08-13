import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Genre, Title, User, Review, Comments


DATA_FILES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comments: 'comments.csv',
}


class Command(BaseCommand):
    """
    Команда для импорта данных.
    """

    help = 'Импортирует данные из CSV файлов в базу данных YaMDb'

    def handle(self, *args, **options):
        """Основной метод для запуска логики импорта."""
        self.data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        for model, filename in DATA_FILES.items():
            self._import_model_data(model, filename)

    def _import_model_data(self, model, filename):
        """Импортирует данные для одной модели."""
        file_path = os.path.join(self.data_dir, filename)

        self.stdout.write(
            self.style.WARNING(f'Импортируем данные из {filename}...')
        )

        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(
                    f'Файл {filename} не найден по пути {file_path}.'
                )
            )
            return

        try:
            with open(file_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    self._create_or_update_model(model, row)

            if model == Title:
                self._import_genre_title_relations()

            self.stdout.write(
                self.style.SUCCESS(f'Успешно загружено: {filename}')
            )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при импорте файла {filename}: {error}'
                )
            )

    def _create_or_update_model(self, model, row):
        """Создаёт или обновляет запись в модели."""
        if model == Title:
            self._create_title(row)
        elif model == Review:
            self._create_review(row)
        elif model == Comments:
            self._create_comment(row)
        else:
            model.objects.get_or_create(
                id=row['id'],
                defaults=row
            )

    def _create_review(self, row):
        """Создаёт отзыв."""
        Review.objects.get_or_create(
            id=row['id'],
            defaults={
                'title_id': row['title_id'],
                'text': row['text'],
                'author_id': row['author'],
                'score': row['score'],
                'pub_date': row['pub_date'],
            }
        )

    def _create_comment(self, row):
        """Создаёт комментарий."""
        Comments.objects.get_or_create(
            id=row['id'],
            defaults={
                'review_id': row['review_id'],
                'text': row['text'],
                'author_id': row['author'],
                'pub_date': row['pub_date'],
            }
        )

    def _create_title(self, row):
        """Создаёт произведение с категорией."""
        category_id = row.get('category')
        category_obj = Category.objects.filter(pk=category_id).first()

        Title.objects.get_or_create(
            id=row['id'],
            defaults={
                'name': row['name'],
                'year': row['year'],
                'description': row.get('description', ''),
                'category': category_obj,
            }
        )

    def _import_genre_title_relations(self):
        """Импортирует связи жанров и произведений."""
        genre_title_path = os.path.join(self.data_dir, 'genre_title.csv')

        if not os.path.exists(genre_title_path):
            return

        self.stdout.write(
            self.style.WARNING('Импортируем связи жанров и произведений...')
        )

        try:
            with open(genre_title_path, encoding='utf-8') as gt_file:
                gt_reader = csv.DictReader(gt_file)
                for row in gt_reader:
                    self._add_genre_to_title(row)
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте связей: {error}')
            )

    def _add_genre_to_title(self, row):
        """Добавляет жанр к произведению."""
        title_id = row.get('title_id')
        genre_id = row.get('genre_id')
        title_obj = Title.objects.filter(pk=title_id).first()
        genre_obj = Genre.objects.filter(pk=genre_id).first()

        if title_obj and genre_obj:
            title_obj.genre.add(genre_obj)
