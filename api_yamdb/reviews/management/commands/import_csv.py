import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Comments, Genre, Review, Title, User

DATA_FILES = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    User: 'users.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comments: 'comments.csv',
    Title.genre.through: 'genre_title.csv',
}


class Command(BaseCommand):
    """Команда для импорта данных из CSV-файлов в базу данных."""

    help = 'Импортирует данные из CSV файлов в базу данных YaMDb'

    def handle(self, *args, **options):
        """Основной метод для запуска логики импорта."""
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        for model, filename in DATA_FILES.items():
            file_path = os.path.join(data_dir, filename)
            if not os.path.exists(file_path):
                continue

            self.stdout.write(self.style.WARNING(f'Импорт {filename}...'))
            objects_to_create = []

            with open(file_path, encoding='utf-8') as csv_file:
                for row in csv.DictReader(csv_file):
                    row_data = {}
                    for key, value in row.items():
                        if key in ('category', 'author'):
                            row_data[f'{key}_id'] = value
                        else:
                            row_data[key] = value
                    objects_to_create.append(model(**row_data))

            model.objects.all().delete()
            model.objects.bulk_create(objects_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f'Успешно загружено: {filename}'
            ))
