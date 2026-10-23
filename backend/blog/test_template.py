from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from .models import Post


class TemplateVideoFieldTests(SimpleTestCase):
    def test_admin_model_field_accepts_local_and_remote_video(self):
        field = Post._meta.get_field('video_url')
        for value in ['/demo/ambient.mp4', '/media/reel.mp4', 'https://example.com/reel.mp4']:
            with self.subTest(value=value):
                self.assertEqual(field.clean(value, None), value)

    def test_admin_model_field_rejects_unsafe_or_ambiguous_urls(self):
        field = Post._meta.get_field('video_url')
        for value in ['javascript:alert(1)', '//example.com/reel.mp4', '/\\example.com/reel.mp4', '/demo/my video.mp4']:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                field.clean(value, None)
