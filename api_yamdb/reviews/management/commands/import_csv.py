"""Кастомная команда Django для импорта данных из CSV-файлов."""

import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Genre, Title

DATA_FILES = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
}


class Command(BaseCommand):
    """Команда для импорта данных."""

    help = 'Импортирует данные из CSV файлов в базу данных YaMDb'

    def handle(self, *args, **options):
        """Основной метод для запуска логики импорта."""
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        for model, filename in DATA_FILES.items():
            file_path = os.path.join(data_dir, filename)
            self.stdout.write(
                self.style.WARNING(f'Импортируем данные из {filename}...')
            )

            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.ERROR(
                        f'Файл {filename} не найден '
                        f'по пути {file_path}! Пропустили.'
                    )
                )
                continue

            try:
                with open(file_path, encoding='utf-8') as csv_file:
                    reader = csv.DictReader(csv_file)

                    for row in reader:
                        if model == Title:
                            category_id = row.get('category')
                            category_obj = Category.objects.filter(
                                pk=category_id
                            ).first()

                            Title.objects.get_or_create(
                                id=row['id'],
                                defaults={
                                    'name': row['name'],
                                    'year': row['year'],
                                    'description': row.get(
                                        'description', ''
                                    ),
                                    'category': category_obj,
                                }
                            )
                        else:
                            model.objects.get_or_create(
                                id=row['id'],
                                defaults=row
                            )

                if model == Title:
                    genre_title_path = os.path.join(
                        data_dir, 'genre_title.csv'
                    )
                    if os.path.exists(genre_title_path):
                        self.stdout.write(
                            self.style.WARNING(
                                'Импортируем связи жанров и произведений...'
                            )
                        )
                        with open(
                            genre_title_path, encoding='utf-8'
                        ) as gt_file:
                            gt_reader = csv.DictReader(gt_file)
                            for row in gt_reader:
                                title_id = row.get('title_id')
                                genre_id = row.get('genre_id')
                                title_obj = Title.objects.filter(
                                    pk=title_id
                                ).first()
                                genre_obj = Genre.objects.filter(
                                    pk=genre_id
                                ).first()
                                if title_obj and genre_obj:
                                    title_obj.genre.add(genre_obj)

                self.stdout.write(
                    self.style.SUCCESS(f'Успешно загружено: {filename}')
                )
            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f'Ошибка при импорте файла {filename}: {error}'
                    )
                )
