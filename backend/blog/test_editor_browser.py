"""Run with PLAYWRIGHT_MODULE pointing to an installed playwright package.

Uses a separate Django test database and temporary upload directory.
"""
import os
import json
import subprocess
import tempfile
from pathlib import Path
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag

from .models import Post, Tag


@tag('browser')
@skipUnless(os.environ.get('PLAYWRIGHT_MODULE'), 'Set PLAYWRIGHT_MODULE to run browser checks')
class ArticleEditorBrowserTests(StaticLiveServerTestCase):
    port = 18001

    def test_edit_restore_upload_and_save_markdown(self):
        user = get_user_model().objects.create_superuser(username='editor-check')
        self.client.force_login(user)
        original = '# 编辑回归检查\n\n敏感地址：`[已打码]`\n\n## 代码\n\n```python\nprint("[REDACTED]")\n```\n\n| 项目 | 值 |\n| --- | --- |\n| 账号 | 已隐藏 |\n'
        post = Post.objects.create(title='编辑器测试副本', slug='editor-test-copy', section='ctf', content=original)
        Tag.objects.create(name='浏览器测试标签', slug='editor-check-tag')
        compatibility_ids = []
        fixture_path = os.environ.get('EDITOR_COMPATIBILITY_FIXTURE')
        if fixture_path:
            for index, sample in enumerate(json.loads(Path(fixture_path).read_text(encoding='utf-8'))):
                copy = Post.objects.create(title=f'兼容性副本 {index}', slug=f'compat-copy-{index}', section='ctf', content=sample['content'])
                compatibility_ids.append(copy.pk)
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            result = subprocess.run(
                ['node', str(Path(__file__).parent / 'browser_tests' / 'article_editor.cjs')],
                env={**os.environ, 'EDITOR_TEST_URL': self.live_server_url,
                     'EDITOR_TEST_SESSION': self.client.cookies[settings.SESSION_COOKIE_NAME].value,
                     'EDITOR_TEST_POST': str(post.pk), 'EDITOR_COMPATIBILITY_IDS': json.dumps(compatibility_ids)},
                capture_output=True, text=True, encoding='utf-8', timeout=160,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        post.refresh_from_db()
        self.assertIn('print("[REDACTED]")', post.content)
        self.assertIn('已隐藏', post.content)
        self.assertIn('恢复后的正文', post.content)
        self.assertIn('/media/content/', post.content)
        self.assertEqual(post.status, 'draft')
