from rest_framework import serializers
from .models import (
    DEFAULT_ABOUT_FACETS,
    DEFAULT_ABOUT_CONTACTS,
    DEFAULT_ABOUT_PAGE,
    DEFAULT_SECTION_PAGES,
    AboutContactLink,
    AboutFacet,
    AboutPage,
    Post,
    Category,
    Tag,
    Comment,
    MediaImage,
    SectionPage,
)


class AboutFacetSerializer(serializers.ModelSerializer):
    """About 页面卡片序列化器"""
    class Meta:
        model = AboutFacet
        fields = ['label', 'title', 'text']


class AboutContactLinkSerializer(serializers.ModelSerializer):
    """About 页面联系方式序列化器"""
    class Meta:
        model = AboutContactLink
        fields = ['name', 'value', 'url']


class AboutPageSerializer(serializers.ModelSerializer):
    """About 页面序列化器"""
    facets = serializers.SerializerMethodField()
    contacts = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields = [
            'brand_name',
            'kicker',
            'hero_title',
            'hero_body',
            'identity_mark',
            'identity_name',
            'identity_meta',
            'current_direction_label',
            'current_direction',
            'contact_label',
            'facets',
            'contacts',
        ]

    def get_facets(self, obj):
        facets = obj.facets.filter(is_visible=True).order_by('sort_order', 'id')
        return AboutFacetSerializer(facets, many=True).data

    def get_contacts(self, obj):
        contacts = obj.contacts.filter(is_visible=True).order_by('sort_order', 'id')
        return AboutContactLinkSerializer(contacts, many=True).data


def get_default_about_payload():
    return {
        **DEFAULT_ABOUT_PAGE,
        'facets': DEFAULT_ABOUT_FACETS,
        'contacts': DEFAULT_ABOUT_CONTACTS,
    }


class SectionPageSerializer(serializers.ModelSerializer):
    """三大分区页面配置序列化器"""
    stat_one = serializers.SerializerMethodField()
    stat_two = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    filters = serializers.SerializerMethodField()

    class Meta:
        model = SectionPage
        fields = [
            'section',
            'eyebrow',
            'title',
            'description',
            'manifesto',
            'index_label',
            'stat_one',
            'stat_two',
            'tags',
            'filters',
            'empty_text',
            'filter_aria_label',
            'extra',
        ]

    def get_stat_one(self, obj):
        return {'value': obj.stat_one_value, 'label': obj.stat_one_label}

    def get_stat_two(self, obj):
        return {'value': obj.stat_two_value, 'label': obj.stat_two_label}

    def get_tags(self, obj):
        return list(
            obj.tags
            .filter(is_visible=True)
            .order_by('sort_order', 'id')
            .values_list('name', flat=True)
        )

    def get_filters(self, obj):
        return [
            {'name': item.name, 'slug': item.slug or None}
            for item in obj.filters.filter(is_visible=True).order_by('sort_order', 'id')
        ]


def get_default_section_page_payload(section):
    page = DEFAULT_SECTION_PAGES[section]
    return {
        'section': section,
        'eyebrow': page['eyebrow'],
        'title': page['title'],
        'description': page['description'],
        'manifesto': page['manifesto'],
        'index_label': page['index_label'],
        'stat_one': page['stat_one'],
        'stat_two': page['stat_two'],
        'tags': page['tags'],
        'filters': page['filters'],
        'empty_text': page['empty_text'],
        'filter_aria_label': page['filter_aria_label'],
        'extra': page['extra'],
    }


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color']


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'section', 'description']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器 (列表用，不含子评论)"""
    class Meta:
        model = Comment
        fields = ['id', 'nickname', 'content', 'parent', 'created_at']


class PostListSerializer(serializers.ModelSerializer):
    """文章列表序列化器 — 不含正文，节省流量"""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover_image',
            'section', 'post_type', 'category', 'tags',
            'is_featured', 'video_url', 'views_count',
            'created_at', 'published_at',
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """文章详情序列化器 — 含正文和已审核评论"""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'cover_image',
            'section', 'post_type', 'category', 'tags',
            'is_featured', 'video_url', 'views_count',
            'created_at', 'updated_at', 'published_at',
            'comments',
        ]

    def get_comments(self, obj):
        # 只返回已审核的顶级评论，嵌套显示子评论
        top_level = obj.comments.filter(is_approved=True, parent__isnull=True)
        return CommentWithRepliesSerializer(top_level, many=True).data


class CommentWithRepliesSerializer(serializers.ModelSerializer):
    """带子评论的评论序列化器"""
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'nickname', 'content', 'created_at', 'replies']

    def get_replies(self, obj):
        replies = obj.replies.filter(is_approved=True)
        return CommentSerializer(replies, many=True).data


class MediaImageSerializer(serializers.ModelSerializer):
    """内容图片序列化器"""
    url = serializers.SerializerMethodField()

    class Meta:
        model = MediaImage
        fields = ['id', 'image', 'url', 'uploaded_at']
        read_only_fields = ['id', 'url', 'uploaded_at']

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.url)
        return obj.url
