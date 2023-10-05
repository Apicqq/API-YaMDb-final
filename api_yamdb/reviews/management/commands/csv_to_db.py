import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User

MODELS_DATA = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Title.genre.through: 'genre_title.csv',
    Comment: 'comments.csv'
}

FIELDS_TO_CHANGE = {
    Review: ['author', 'author_id'],
    Title: ['category', 'category_id'],
    Comment: ['author', 'author_id'],
}


class Command(BaseCommand):
    """Команда, позволяющая загрузить данные из CSV-файлов в БД.
    Использование:
    1. Очистить текущую базу данных.
    2. Применить миграции.
    3. Запустить команду: python manage.py csv_to_db.
    """

    help = 'Загрузка данных в базу данных из CSV-файлов.'

    def handle(self, *args, **options):
        for model, csv_file in MODELS_DATA.items():
            with open(
                    f'{settings.BASE_DIR}/static/data/{csv_file}', 'r',
                    encoding="utf-8",
            ) as file:
                reader = csv.DictReader(file)
                records = []
                for row in reader:
                    if model in FIELDS_TO_CHANGE:
                        row = {
                            field_from_csv.replace(
                                FIELDS_TO_CHANGE[model][0],
                                FIELDS_TO_CHANGE[model][1]): field_to_table for
                            field_from_csv, field_to_table in row.items()
                        }
                    records.append(model(**row))
            model.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(
                f'Данные объекта {model.__name__} загружены.'
            ))
