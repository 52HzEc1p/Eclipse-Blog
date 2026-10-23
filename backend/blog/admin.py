from django import forms
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from urllib.parse import parse_qs, urlparse

from .models import (
    AboutContactLink,
    AboutFacet,
    AboutPage,
    Category,
    Comment,
    MediaImage,
    Post,
    PostStatus,
    SectionPage,
    SectionPageFilter,
    SectionPageTag,
    Tag,
)


admin.site.site_header = 'Eclipse Content Studio'
admin.site.site_title = 'Eclipse Admin'
admin.site.index_title = '内容工作台'


class AboutFacetInline(admin.TabularInline):
    model = AboutFacet
    extra = 0
    fields = ['label', 'title', 'text', 'sort_order', 'is_visible']


class AboutContactLinkInline(admin.TabularInline):
    model = AboutContactLink
    extra = 0
    fields = ['name', 'value', 'url', 'sort_order', 'is_visible']


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'kicker', 'updated_at']
    readonly_fields = ['updated_at']
    inlines = [AboutFacetInline, AboutContactLinkInline]
    save_on_top = True
    fieldsets = (
        ('首屏内容', {
            'fields': ('brand_name', 'kicker', 'hero_title', 'hero_body'),
        }),
        ('身份卡片', {
            'fields': ('identity_mark', 'identity_name', 'identity_meta'),
        }),
        ('正在做的事', {
            'fields': ('current_direction_label', 'current_direction'),
        }),
        ('Contact', {
            'fields': ('contact_label',),
        }),
        ('系统信息', {
            'classes': ('collapse',),
            'fields': ('updated_at',),
        }),
    )
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={
                'rows': 5,
                'style': 'font-size: 14px; line-height: 1.7;',
            })
        }
    }


class SectionPageTagInline(admin.TabularInline):
    model = SectionPageTag
    extra = 0
    fields = ['name', 'sort_order', 'is_visible']


class SectionPageFilterInline(admin.TabularInline):
    model = SectionPageFilter
    extra = 0
    fields = ['name', 'slug', 'sort_order', 'is_visible']


@admin.register(SectionPage)
class SectionPageAdmin(admin.ModelAdmin):
    list_display = ['section', 'title', 'eyebrow', 'updated_at']
    list_filter = ['section']
    search_fields = ['title', 'description', 'manifesto']
    readonly_fields = ['updated_at']
    inlines = [SectionPageTagInline, SectionPageFilterInline]
    save_on_top = True
    fieldsets = (
        ('基础展示', {
            'fields': ('section', 'eyebrow', 'title', 'description', 'manifesto', 'index_label', 'empty_text', 'filter_aria_label'),
        }),
        ('统计文案', {
            'fields': ('stat_one_value', 'stat_one_label', 'stat_two_value', 'stat_two_label'),
        }),
        ('页面专属文案 JSON', {
            'fields': ('extra',),
            'description': '用于 Projects craft cards、Gallery timeline/loadout/run log 等页面特有文字。',
        }),
        ('系统信息', {
            'classes': ('collapse',),
            'fields': ('updated_at',),
        }),
    )
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={
                'rows': 5,
                'style': 'font-size: 14px; line-height: 1.7;',
            })
        },
        models.JSONField: {
            'widget': forms.Textarea(attrs={
                'rows': 18,
                'style': 'font-family: Cascadia Code, JetBrains Mono, Consolas, monospace; font-size: 13px; line-height: 1.55;',
            })
        },
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'section', 'description']
    list_filter = ['section']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'color_preview']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='预览')
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:52px;height:18px;border-radius:4px;background:{};border:1px solid rgba(0,0,0,.18);"></span>',
            obj.color,
        )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'section',
        'post_type',
        'status',
        'is_featured',
        'views_count',
        'published_at',
        'updated_at',
    ]
    list_filter = ['section', 'post_type', 'status', 'is_featured', 'category', 'tags']
    list_editable = ['status', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    readonly_fields = [
        'cover_preview',
        'video_preview',
        'views_count',
        'created_at',
        'updated_at',
    ]
    save_on_top = True
    actions = ['publish_posts', 'move_to_draft', 'mark_featured', 'unmark_featured']
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={
                'rows': 24,
                'style': 'font-family: Cascadia Code, JetBrains Mono, Consolas, monospace; font-size: 14px; line-height: 1.7;',
            })
        }
    }

    fieldsets = (
        ('基础内容', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'cover_image', 'cover_preview'),
        }),
        ('分类与展示', {
            'fields': ('section', 'post_type', 'category', 'tags'),
        }),
        ('视频设置', {
            'fields': ('video_url', 'video_preview'),
            'description': '视频内容选择“视频”类型后，填写 B 站、YouTube、Vimeo 或可直接播放的视频地址。',
        }),
        ('发布设置', {
            'fields': ('status', 'is_featured', 'published_at'),
        }),
        ('系统信息', {
            'classes': ('collapse',),
            'fields': ('views_count', 'created_at', 'updated_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.status == PostStatus.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.display(description='封面预览')
    def cover_preview(self, obj):
        if not obj.cover_image:
            return '上传封面图后显示预览'
        return format_html(
            '<img src="{}" style="max-width:420px;max-height:236px;border-radius:8px;object-fit:cover;border:1px solid rgba(0,0,0,.12);" />',
            obj.cover_image.url,
        )

    @admin.display(description='视频预览')
    def video_preview(self, obj):
        if not obj.video_url:
            return '填写视频链接后显示预览'

        embed_url = self.get_video_embed_url(obj.video_url)
        link_html = format_html(
            '<p style="margin:8px 0 0;"><a href="{}" target="_blank" rel="noopener">打开原链接</a></p>',
            obj.video_url,
        )
        if not embed_url:
            return format_html(
                '<p style="margin:0 0 8px;color:#6b7280;">暂不能内嵌预览，但前台会保留原链接。</p>{}',
                link_html,
            )

        if embed_url['type'] == 'direct':
            return format_html(
                '<video src="{}" controls preload="metadata" style="width:100%;max-width:720px;aspect-ratio:16/9;background:#000;border-radius:8px;"></video>{}',
                embed_url['src'],
                link_html,
            )

        return format_html(
            '<div style="width:100%;max-width:720px;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000;">'
            '<iframe src="{}" style="width:100%;height:100%;border:0;" allowfullscreen loading="lazy"></iframe>'
            '</div>{}',
            embed_url['src'],
            link_html,
        )

    def get_video_embed_url(self, url):
        parsed = urlparse(url)
        host = parsed.netloc.lower().removeprefix('www.')
        path = parsed.path.strip('/')
        query = parse_qs(parsed.query)

        if host in {'youtube.com', 'm.youtube.com'} and path == 'watch':
            video_id = query.get('v', [''])[0]
            if video_id:
                return {'type': 'iframe', 'src': f'https://www.youtube.com/embed/{video_id}'}
        if host == 'youtu.be' and path:
            video_id = path.split('/')[0]
            return {'type': 'iframe', 'src': f'https://www.youtube.com/embed/{video_id}'}
        if host == 'youtube.com' and path.startswith('embed/'):
            return {'type': 'iframe', 'src': url}

        if host.endswith('bilibili.com') and path.startswith('video/'):
            bvid = path.split('/')[1] if len(path.split('/')) > 1 else ''
            if bvid.startswith('BV'):
                return {'type': 'iframe', 'src': f'https://player.bilibili.com/player.html?bvid={bvid}&high_quality=1'}
        if host == 'player.bilibili.com':
            return {'type': 'iframe', 'src': url}

        if host == 'vimeo.com' and path:
            video_id = path.split('/')[0]
            if video_id.isdigit():
                return {'type': 'iframe', 'src': f'https://player.vimeo.com/video/{video_id}'}
        if host == 'player.vimeo.com' and path.startswith('video/'):
            return {'type': 'iframe', 'src': url}

        if parsed.path.lower().endswith(('.mp4', '.webm', '.mov')):
            return {'type': 'direct', 'src': url}

        return None

    class Media:
        css = {
            'all': (
                'blog/vendor/easymde/easymde.min.css',
                'blog/admin/markdown_editor.css',
            ),
        }
        js = (
            'blog/vendor/easymde/easymde.min.js',
            'blog/admin/post_markdown_editor.js',
        )

    @admin.action(description='发布选中的内容')
    def publish_posts(self, request, queryset):
        queryset.update(status=PostStatus.PUBLISHED, published_at=timezone.now())

    @admin.action(description='移回草稿')
    def move_to_draft(self, request, queryset):
        queryset.update(status=PostStatus.DRAFT)

    @admin.action(description='设为精选')
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='取消精选')
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['nickname', 'content', 'post__title']
    actions = ['approve_comments', 'reject_comments']

    @admin.action(description='审核通过')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='取消通过')
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(MediaImage)
class MediaImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'uploaded_at', 'image_url']
    readonly_fields = ['uploaded_at', 'image_url', 'markdown_url', 'preview']
    fields = ['image', 'preview', 'image_url', 'markdown_url', 'uploaded_at']
    list_per_page = 30

    @admin.display(description='预览')
    def preview(self, obj):
        if not obj.pk:
            return '上传后显示预览'
        return format_html(
            '<img src="{}" style="max-width:360px;max-height:220px;border-radius:6px;object-fit:cover;" />',
            obj.url,
        )

    @admin.display(description='图片 URL')
    def image_url(self, obj):
        if not obj.pk:
            return '上传后生成 URL'
        return format_html(
            '<input value="{}" readonly style="width:100%;font-family:monospace;padding:6px 8px;" />',
            obj.url,
        )

    @admin.display(description='Markdown 引用')
    def markdown_url(self, obj):
        if not obj.image:
            return '上传后生成 Markdown 引用'
        markdown = f'![图片]({obj.url})'
        return format_html(
            '<input value="{}" readonly style="width:100%;font-family:monospace;padding:6px 8px;" />',
            markdown,
        )
