from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from pathlib import Path
from .models import AboutPage, DEFAULT_SECTION_PAGES, Post, Category, Tag, MediaImage, SectionPage
from .serializers import (
    AboutPageSerializer,
    SectionPageSerializer,
    PostListSerializer, PostDetailSerializer,
    CategorySerializer, TagSerializer,
    MediaImageSerializer,
    get_default_about_payload,
    get_default_section_page_payload,
)


class AboutPageView(APIView):
    """
    About 页面 API
    - GET /api/about/  -> 前台 About 页面内容
    """
    def get(self, request):
        about_page = AboutPage.objects.prefetch_related('facets').order_by('-updated_at', '-id').first()
        if not about_page:
            return Response(get_default_about_payload())
        return Response(AboutPageSerializer(about_page).data)


class SectionPageView(APIView):
    """
    三大分区页面配置 API
    - GET /api/section-pages/{section}/ -> Articles / Projects / Gallery 页面文案
    """
    def get(self, request, section):
        if section not in DEFAULT_SECTION_PAGES:
            return Response({'detail': '未知板块'}, status=status.HTTP_404_NOT_FOUND)

        section_page = SectionPage.objects.prefetch_related('tags', 'filters').filter(section=section).first()
        if not section_page:
            return Response(get_default_section_page_payload(section))
        return Response(SectionPageSerializer(section_page).data)


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    文章 API
    - GET /api/posts/          → 文章列表 (支持 ?section=ctf 过滤)
    - GET /api/posts/{slug}/   → 文章详情 (slug 查找)
    - GET /api/posts/featured/ → 精选文章
    """
    lookup_field = 'slug'
    queryset = Post.objects.filter(status='published')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # ?section=ctf 按板块过滤
        section = self.request.query_params.get('section')
        if section:
            qs = qs.filter(section=section)
        # ?category=web-sec 按分类过滤
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        # ?tag=sqli 按标签过滤
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        viewed_posts = request.session.get('viewed_posts', {})
        key = str(instance.pk)
        now = timezone.now()
        last_viewed = viewed_posts.get(key)
        should_count_view = True

        if last_viewed:
            try:
                should_count_view = now - timezone.datetime.fromisoformat(last_viewed) > timedelta(hours=12)
            except ValueError:
                should_count_view = True

        if should_count_view:
            instance.increment_views()
            viewed_posts[key] = now.isoformat()
            request.session['viewed_posts'] = viewed_posts
            request.session.modified = True
            # 重新从数据库获取更新后的 views_count
            instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """精选文章: GET /api/posts/featured/"""
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = PostListSerializer(featured, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    分类 API
    - GET /api/categories/          → 全部分类
    - GET /api/categories/?section=ctf → 按板块筛选分类
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        section = self.request.query_params.get('section')
        if section:
            qs = qs.filter(section=section)
        return qs


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    标签 API
    - GET /api/tags/ → 全部标签
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class MediaImageViewSet(viewsets.ModelViewSet):
    """
    内容图片上传 API
    - POST /api/images/ → 上传图片，返回 URL
    """
    serializer_class = MediaImageSerializer
    queryset = MediaImage.objects.all()
    http_method_names = ['post', 'get', 'head', 'options']
    # 个人站：图片库只允许管理员读写，避免匿名上传刷爆存储
    permission_classes = [IsAdminUser]


@staff_member_required
@require_POST
def admin_markdown_image_upload(request):
    uploaded = request.FILES.get('image')
    if not uploaded:
        return JsonResponse({'error': '请选择要上传的图片'}, status=400)
    if not uploaded.content_type.startswith('image/'):
        return JsonResponse({'error': '只能上传图片文件'}, status=400)

    media_image = MediaImage.objects.create(image=uploaded)
    url = media_image.url
    alt_text = Path(uploaded.name).stem or '图片'
    return JsonResponse({
        'url': url,
        'markdown': f'![{alt_text}]({url})',
    })
