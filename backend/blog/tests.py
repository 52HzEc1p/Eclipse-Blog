from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .admin import MediaImageAdmin, PostAdmin
from .models import (
    AboutContactLink,
    AboutFacet,
    AboutPage,
    MediaImage,
    Post,
    PostStatus,
    PostType,
    Section,
    SectionPage,
    SectionPageFilter,
    SectionPageTag,
)
from django.utils import timezone


class AboutPageApiTests(TestCase):
    def test_about_endpoint_returns_default_page_content(self):
        response = self.client.get('/api/about/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['brand_name'], 'Eclipse')
        self.assertEqual(payload['hero_title'], '你好，这里是你的名字。')
        self.assertIn('current_direction', payload)
        self.assertEqual(payload['current_direction_label'], '正在做的事')
        self.assertEqual(payload['contact_label'], '找到你')
        self.assertEqual(
            [contact['name'] for contact in payload['contacts']],
            ['GitHub', 'Website'],
        )
        self.assertEqual(len(payload['facets']), 3)
        self.assertNotIn('Name', [facet['label'] for facet in payload['facets']])
        self.assertEqual(
            [facet['title'] for facet in payload['facets']],
            ['Articles', 'Projects', 'Gallery'],
        )

    def test_about_endpoint_uses_editable_admin_content_and_hidden_facets(self):
        about_page = AboutPage.objects.create(
            brand_name='Moonlit Studio',
            kicker='ABOUT / MOON',
            hero_title='新的标题',
            hero_body='新的简介',
            identity_mark='Moon',
            identity_name='Studio',
            identity_meta='Editing / Notes',
            current_direction_label='Now Building',
            current_direction='新的 Current Direction',
            contact_label='Find Me',
        )
        AboutFacet.objects.create(
            about_page=about_page,
            label='Visible',
            title='会展示的卡片',
            text='后台可以修改这里的内容。',
            sort_order=1,
        )
        AboutFacet.objects.create(
            about_page=about_page,
            label='Hidden',
            title='多余卡片',
            text='这个不应该出现在前台。',
            sort_order=2,
            is_visible=False,
        )
        AboutContactLink.objects.create(
            about_page=about_page,
            name='GitHub',
            value='代码和项目',
            url='https://github.com/example',
            sort_order=1,
        )
        AboutContactLink.objects.create(
            about_page=about_page,
            name='Hidden Contact',
            value='不展示',
            url='https://example.com/hidden',
            sort_order=2,
            is_visible=False,
        )

        response = self.client.get('/api/about/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['brand_name'], 'Moonlit Studio')
        self.assertEqual(payload['hero_title'], '新的标题')
        self.assertEqual(payload['current_direction_label'], 'Now Building')
        self.assertEqual(payload['current_direction'], '新的 Current Direction')
        self.assertEqual(payload['contact_label'], 'Find Me')
        self.assertEqual(payload['contacts'], [
            {
                'name': 'GitHub',
                'value': '代码和项目',
                'url': 'https://github.com/example',
            }
        ])
        self.assertEqual(payload['facets'], [
            {
                'label': 'Visible',
                'title': '会展示的卡片',
                'text': '后台可以修改这里的内容。',
            }
        ])


class SectionPageApiTests(TestCase):
    def test_section_page_endpoint_returns_default_editable_copy(self):
        response = self.client.get('/api/section-pages/ctf/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['section'], 'ctf')
        self.assertEqual(payload['title'], 'Articles')
        self.assertEqual(payload['eyebrow'], '// article archive')
        self.assertEqual(payload['stat_one'], {'value': 'Aa', 'label': 'ideas & stories'})
        self.assertEqual(payload['filters'][0], {'name': 'All', 'slug': None})
        self.assertIn('notes', payload['tags'])

    def test_section_page_endpoint_uses_admin_copy_and_hides_items(self):
        section_page = SectionPage.objects.get(section=Section.EDITING)
        section_page.title = 'New Frame'
        section_page.eyebrow = 'custom eyebrow'
        section_page.description = 'custom description'
        section_page.manifesto = 'custom manifesto'
        section_page.index_label = 'CUSTOM / INDEX'
        section_page.stat_one_value = 'S1'
        section_page.stat_one_label = 'stat one'
        section_page.stat_two_value = 'S2'
        section_page.stat_two_label = 'stat two'
        section_page.empty_text = 'custom empty'
        section_page.filter_aria_label = 'custom filter label'
        section_page.extra = {'craft_title': 'Custom Craft'}
        section_page.save()
        section_page.tags.update(is_visible=False)
        section_page.filters.update(is_visible=False)
        SectionPageTag.objects.create(section_page=section_page, name='visible tag', sort_order=1)
        SectionPageTag.objects.create(section_page=section_page, name='hidden tag', sort_order=2, is_visible=False)
        SectionPageFilter.objects.create(section_page=section_page, name='All Custom', slug='', sort_order=1)
        SectionPageFilter.objects.create(section_page=section_page, name='Hidden Filter', slug='hidden', sort_order=2, is_visible=False)

        response = self.client.get('/api/section-pages/editing/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['title'], 'New Frame')
        self.assertEqual(payload['stat_two'], {'value': 'S2', 'label': 'stat two'})
        self.assertEqual(payload['tags'], ['visible tag'])
        self.assertEqual(payload['filters'], [{'name': 'All Custom', 'slug': None}])
        self.assertEqual(payload['extra']['craft_title'], 'Custom Craft')


class PostViewCountTests(TestCase):
    def test_repeated_post_detail_views_from_same_session_count_once(self):
        post = Post.objects.create(
            title='SQL note',
            slug='sql-note',
            section=Section.CTF,
            status=PostStatus.PUBLISHED,
            published_at=timezone.now(),
        )

        first = self.client.get('/api/posts/sql-note/')
        second = self.client.get('/api/posts/sql-note/')
        post.refresh_from_db()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(post.views_count, 1)


class PostPaginationTests(TestCase):
    def test_posts_list_respects_page_size_query_param(self):
        for index in range(9):
            Post.objects.create(
                title=f'CTF note {index}',
                slug=f'ctf-note-{index}',
                section=Section.CTF,
                status=PostStatus.PUBLISHED,
                published_at=timezone.now(),
            )

        response = self.client.get('/api/posts/?section=ctf&page_size=8')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 9)
        self.assertEqual(len(payload['results']), 8)


class PostAdminWorkspaceTests(TestCase):
    def setUp(self):
        self.post_admin = PostAdmin(Post, admin.site)

    def test_video_preview_embeds_supported_video_links(self):
        post = Post(
            title='Video note',
            section=Section.EDITING,
            post_type=PostType.VIDEO,
            video_url='https://www.bilibili.com/video/BV1xx411c7mD/',
        )

        preview = self.post_admin.video_preview(post)

        self.assertIn('iframe', preview)
        self.assertIn('player.bilibili.com/player.html?bvid=BV1xx411c7mD', preview)
        self.assertIn('打开原链接', preview)

    def test_cover_preview_renders_uploaded_cover(self):
        post = Post(
            title='Article note',
            section=Section.CTF,
            post_type=PostType.ARTICLE,
            cover_image='covers/2026/05/sample.jpg',
        )

        preview = self.post_admin.cover_preview(post)

        self.assertIn('img', preview)
        self.assertIn('/media/covers/2026/05/sample.jpg', preview)

    def test_post_admin_groups_video_fields_separately(self):
        fieldset_names = [name for name, _ in self.post_admin.fieldsets]

        self.assertIn('视频设置', fieldset_names)
        self.assertIn('video_preview', self.post_admin.readonly_fields)

    def test_post_admin_loads_markdown_editor_assets(self):
        media_js = list(self.post_admin.media._js)
        media_css = self.post_admin.media._css.get('all', [])

        self.assertIn('blog/vendor/easymde/easymde.min.js', media_js)
        self.assertIn('blog/admin/post_markdown_editor.js', media_js)
        self.assertIn('blog/vendor/easymde/easymde.min.css', media_css)
        self.assertIn('blog/admin/markdown_editor.css', media_css)

    def test_markdown_editor_script_defines_live_preview_workspace(self):
        script_path = settings.BASE_DIR / 'blog' / 'static' / 'blog' / 'admin' / 'post_markdown_editor.js'
        script = script_path.read_text(encoding='utf-8')

        self.assertIn('markdown-editor-workspace', script)
        self.assertIn('markdown-live-preview', script)
        self.assertIn('schedulePreviewRender', script)


class MediaImageAdminWorkspaceTests(TestCase):
    def setUp(self):
        self.image_admin = MediaImageAdmin(MediaImage, admin.site)

    def test_markdown_url_is_ready_to_copy_after_upload(self):
        media_image = MediaImage(image='content/2026/05/sample.png')

        markdown = self.image_admin.markdown_url(media_image)

        self.assertIn('![图片](/media/content/2026/05/sample.png)', markdown)
        self.assertIn('readonly', markdown)


class AdminImageUploadTests(TestCase):
    def setUp(self):
        self.url = '/admin/blog/upload-image/'
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password',
        )

    def test_staff_can_upload_image_for_markdown_editor(self):
        self.client.force_login(self.user)
        image = SimpleUploadedFile(
            'screen.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
            content_type='image/png',
        )

        response = self.client.post(self.url, {'image': image})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['url'].startswith('/media/content/'))
        self.assertEqual(payload['markdown'], f'![screen]({payload["url"]})')

    def test_anonymous_users_cannot_upload_editor_images(self):
        image = SimpleUploadedFile(
            'screen.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
            content_type='image/png',
        )

        response = self.client.post(self.url, {'image': image})

        self.assertEqual(response.status_code, 302)

    def test_upload_requires_an_image_file(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], '请选择要上传的图片')
