"""Load fictional demo content without copying any production database."""
import json
import shutil
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from blog.models import Post, Category, Tag


class Command(BaseCommand):
    help = 'Load sample articles; existing articles and admin accounts are never overwritten.'

    @transaction.atomic
    def handle(self, *args, **options):
        data = json.loads((Path(settings.BASE_DIR) / 'demo/posts.json').read_text(encoding='utf8'))
        demo_media = Path(settings.MEDIA_ROOT) / 'demo'
        demo_media.mkdir(parents=True, exist_ok=True)
        for name in ['notes.png', 'frames.png', 'play.png']:
            destination = demo_media / name
            if not destination.exists():
                shutil.copy2(Path(settings.BASE_DIR).parent / 'frontend/public/demo' / name, destination)
        tag, _ = Tag.objects.get_or_create(slug='demo', defaults={'name': '示例', 'color': '#22d3ee'})
        created = 0
        for item in data:
            item = dict(item)
            category_data = item.pop('category')
            category, _ = Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults={'name': category_data['name'], 'section': item['section']},
            )
            slug = item.pop('slug')
            post, is_new = Post.objects.get_or_create(
                slug=slug,
                defaults={**item, 'category': category, 'status': 'published', 'published_at': timezone.now()},
            )
            if is_new:
                post.tags.add(tag)
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} demo posts; existing content preserved.'))
