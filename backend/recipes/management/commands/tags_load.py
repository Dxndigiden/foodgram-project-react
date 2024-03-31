import csv
import logging

from django.core.management.base import BaseCommand

from recipes.models import Tag

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/tags.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            tags_to_create = []

            for row in reader:
                name, color, slug = row
                if name:
                    tag = Tag(name=name, color=color, slug=slug)
                    tags_to_create.append(tag)

            Tag.objects.bulk_create(tags_to_create)
            logger.info('Теги успешно подгружены!')
