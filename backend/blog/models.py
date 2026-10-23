from django.db import models
from django.utils.text import slugify
import uuid
from .validators import validate_video_url


DEFAULT_ABOUT_PAGE = {'brand_name': 'Eclipse',
 'kicker': 'ABOUT / DEMO',
 'hero_title': '你好，这里是你的名字。',
 'hero_body': '这是一段作者介绍示例。你可以在这里介绍自己正在做的事、感兴趣的领域，以及希望通过这个博客分享的内容。',
 'identity_mark': 'YOU',
 'identity_name': 'Your Name',
 'identity_meta': 'Your role / Your interests',
 'current_direction_label': '正在做的事',
 'current_direction': '用一小段文字介绍近期的计划、正在推进的项目，或希望继续探索的方向。这里的示例文字可以全部替换。',
 'contact_label': '找到你'}

DEFAULT_ABOUT_FACETS = [{'label': '01 / WRITE', 'title': 'Articles', 'text': '分享知识、记录学习，也可以写日常随笔。用文章介绍你关注的话题。'},
 {'label': '02 / CREATE', 'title': 'Projects', 'text': '展示已经完成或正在进行的作品，补充项目背景、过程和成果。'},
 {'label': '03 / COLLECT', 'title': 'Gallery', 'text': '收集影像、片段与灵感，让值得保存的画面有一个展示的位置。'}]

DEFAULT_ABOUT_CONTACTS = [{'name': 'GitHub', 'value': '你的代码主页（示例链接）', 'url': 'https://github.com/'},
 {'name': 'Website', 'value': '你的其他网站（示例链接）', 'url': 'https://example.com/'}]


DEFAULT_SECTION_PAGES = {'ctf': {'title': 'Articles',
         'eyebrow': '// article archive',
         'description': '文章与笔记的示例栏目。这里可以放学习记录、经验分享和日常随笔，按照自己的主题慢慢整理。',
         'manifesto': '从一个问题、一段经历或一个想法开始。用文字、代码和配图说明过程，让每篇文章都能独立阅读。',
         'index_label': 'ARTICLE / NOTE',
         'stat_one': {'value': 'Aa', 'label': 'ideas & stories'},
         'stat_two': {'value': 'MD', 'label': 'article archive'},
         'tags': ['notes', 'ideas', 'guides', 'learning', 'journal'],
         'filters': [{'name': 'All', 'slug': None},
                     {'name': 'Notes', 'slug': 'notes'},
                     {'name': 'Guides', 'slug': 'guides'}],
         'empty_text': '暂时没有匹配的文章',
         'filter_aria_label': '文章分类',
         'extra': {}},
 'editing': {'title': 'Projects',
             'eyebrow': 'selected projects',
             'description': '作品展示的示例栏目。用一段演示视频介绍项目，再写下它的背景、制作过程和最终成果。',
             'manifesto': '',
             'index_label': 'PROJECT',
             'stat_one': {'value': '01', 'label': 'selected work'},
             'stat_two': {'value': 'Demo', 'label': 'project showcase'},
             'tags': ['projects', 'design', 'experiments', 'process', 'showcase'],
             'filters': [{'name': 'All', 'slug': None}],
             'empty_text': '暂时没有匹配的作品',
             'filter_aria_label': '作品分类',
             'extra': {'panel_topline_left': 'PROJECT / 01',
                       'panel_topline_right': 'demo showcase',
                       'featured_empty_label': 'NO PROJECTS',
                       'featured_empty_title': '暂时没有可展示的作品',
                       'featured_empty_body': '发布第一条带视频的作品后，它会出现在这里。',
                       'loading_title': '正在读取作品',
                       'loading_label': 'loading projects',
                       'craft_eyebrow': '// project notes',
                       'craft_title': 'Behind the Project',
                       'craft_cards': [{'id': 'idea',
                                        'title': 'The Idea',
                                        'body': '介绍项目从何而来，以及你希望解决的问题。',
                                        'meta': ['idea', 'context']},
                                       {'id': 'process',
                                        'title': 'The Process',
                                        'body': '记录设计、尝试和调整，补充关键的过程图片。',
                                        'meta': ['draft', 'iteration']},
                                       {'id': 'result',
                                        'title': 'The Result',
                                        'body': '展示完成后的成果，也可以写下下一步计划。',
                                        'meta': ['demo', 'next step']}]}},
 'games': {'title': 'Gallery',
           'eyebrow': 'visual collection',
           'description': '影像与灵感的示例栏目。用短片、动态画面和简短说明，整理想要保存的片段。',
           'manifesto': '',
           'index_label': 'GALLERY',
           'stat_one': {'value': '', 'label': ''},
           'stat_two': {'value': '', 'label': ''},
           'tags': ['visuals', 'moments', 'motion', 'inspiration', 'collection'],
           'filters': [{'name': 'All', 'slug': None}],
           'empty_text': '暂时没有匹配的影像',
           'filter_aria_label': '影像分类',
           'extra': {'background_label': 'DEMO BACKGROUND',
                     'voice_label': 'COLLECTION NOTES',
                     'voice_body': '为每个片段写一段简短说明：拍摄背景、创作想法，或收藏它的原因。',
                     'featured_empty_label': 'NO MEDIA',
                     'featured_empty_title': '暂时没有可展示的影像',
                     'featured_empty_body': '发布第一条带视频的内容后，它会出现在这里。',
                     'loadout_label': 'TOPICS',
                     'run_log_label': 'COLLECTION',
                     'loading_text': '正在读取影像...',
                     'no_more_text': '暂无更多影像。',
                     'timeline': [{'year': '01', 'role': 'First Collection', 'studio': '示例合集'},
                                  {'year': '02', 'role': 'Work in Progress', 'studio': '创作片段'},
                                  {'year': '03', 'role': 'Small Moments', 'studio': '日常灵感'}]}}}


class Section(models.TextChoices):
    """博客板块"""
    CTF = 'ctf', '文章'
    EDITING = 'editing', '作品'
    GAMES = 'games', '影像'


class PostType(models.TextChoices):
    """文章类型"""
    ARTICLE = 'article', '图文'
    GALLERY = 'gallery', '图片集'
    VIDEO = 'video', '视频'


class PostStatus(models.TextChoices):
    """文章状态"""
    DRAFT = 'draft', '草稿'
    PUBLISHED = 'published', '已发布'


class Category(models.Model):
    """分类"""
    name = models.CharField('分类名', max_length=50)
    slug = models.SlugField('URL标识', max_length=50, unique=True)
    section = models.CharField('所属板块', max_length=10, choices=Section.choices)
    description = models.TextField('描述', blank=True, default='')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']

    def __str__(self):
        return f'[{self.get_section_display()}] {self.name}'


class Tag(models.Model):
    """标签"""
    name = models.CharField('标签名', max_length=30)
    slug = models.SlugField('URL标识', max_length=30, unique=True)
    color = models.CharField('颜色', max_length=7, default='#6366f1',
                             help_text='HEX 色值，如 #22d3ee')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    """文章"""
    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL标识', max_length=200, unique=True, blank=True)
    excerpt = models.TextField('摘要', max_length=300, blank=True, default='')
    content = models.TextField('正文(Markdown)', blank=True, default='')
    cover_image = models.ImageField('封面图', upload_to='covers/%Y/%m/', blank=True)

    section = models.CharField('板块', max_length=10, choices=Section.choices)
    post_type = models.CharField('文章类型', max_length=10, choices=PostType.choices,
                                  default=PostType.ARTICLE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                  null=True, blank=True, verbose_name='分类',
                                  related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签',
                                   related_name='posts')

    status = models.CharField('状态', max_length=10, choices=PostStatus.choices,
                               default=PostStatus.DRAFT)
    is_featured = models.BooleanField('精选', default=False)
    video_url = models.CharField('视频链接', max_length=200, blank=True, default='',
                                 validators=[validate_video_url],
                                 help_text='视频文章可填写 https:// 链接或 /demo/example.mp4 这样的本地路径')

    views_count = models.PositiveIntegerField('阅读量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_section_display()}] {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = uuid.uuid4().hex[:8]
            self.slug = f'{base_slug}-{uuid.uuid4().hex[:6]}'
        super().save(*args, **kwargs)

    def increment_views(self):
        """阅读量 +1"""
        self.views_count = models.F('views_count') + 1
        self.save(update_fields=['views_count'])


class MediaImage(models.Model):
    """内容图片 — 用于 markdown 文章中插入图片"""
    image = models.ImageField('图片', upload_to='content/%Y/%m/')
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        verbose_name = '内容图片'
        verbose_name_plural = '内容图片'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.image.name} ({self.uploaded_at.strftime("%Y-%m-%d %H:%M")})'

    @property
    def url(self):
        return self.image.url


class AboutPage(models.Model):
    """About 页面内容"""
    brand_name = models.CharField('站点名', max_length=80, default=DEFAULT_ABOUT_PAGE['brand_name'])
    kicker = models.CharField('顶部标识', max_length=120, default=DEFAULT_ABOUT_PAGE['kicker'])
    hero_title = models.CharField('主标题', max_length=120, default=DEFAULT_ABOUT_PAGE['hero_title'])
    hero_body = models.TextField('主介绍', default=DEFAULT_ABOUT_PAGE['hero_body'])
    identity_mark = models.CharField('身份卡标记', max_length=40, default=DEFAULT_ABOUT_PAGE['identity_mark'])
    identity_name = models.CharField('身份卡名称', max_length=80, default=DEFAULT_ABOUT_PAGE['identity_name'])
    identity_meta = models.CharField('身份卡补充', max_length=120, default=DEFAULT_ABOUT_PAGE['identity_meta'])
    current_direction_label = models.CharField(
        'Current Direction 标签',
        max_length=80,
        default=DEFAULT_ABOUT_PAGE['current_direction_label'],
    )
    current_direction = models.TextField('正在做的事', default=DEFAULT_ABOUT_PAGE['current_direction'])
    contact_label = models.CharField('Contact 标签', max_length=80, default=DEFAULT_ABOUT_PAGE['contact_label'])
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = 'About 页面'
        verbose_name_plural = 'About 页面'

    def __str__(self):
        return self.brand_name


class AboutFacet(models.Model):
    """About 页面卡片"""
    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        verbose_name='About 页面',
        related_name='facets',
    )
    label = models.CharField('标签', max_length=40)
    title = models.CharField('标题', max_length=80)
    text = models.TextField('内容')
    sort_order = models.PositiveSmallIntegerField('排序', default=0)
    is_visible = models.BooleanField('前台显示', default=True)

    class Meta:
        verbose_name = 'About 卡片'
        verbose_name_plural = 'About 卡片'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.label} - {self.title}'


class AboutContactLink(models.Model):
    """About 页面联系方式"""
    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        verbose_name='About 页面',
        related_name='contacts',
    )
    name = models.CharField('名称', max_length=60)
    value = models.CharField('说明', max_length=120)
    url = models.URLField('链接')
    sort_order = models.PositiveSmallIntegerField('排序', default=0)
    is_visible = models.BooleanField('前台显示', default=True)

    class Meta:
        verbose_name = 'About 联系方式'
        verbose_name_plural = 'About 联系方式'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class SectionPage(models.Model):
    """三大分区页面展示文案"""
    section = models.CharField('板块', max_length=10, choices=Section.choices, unique=True)
    eyebrow = models.CharField('眉标', max_length=120, blank=True, default='')
    title = models.CharField('标题', max_length=120)
    description = models.TextField('描述', blank=True, default='')
    manifesto = models.TextField('侧栏宣言', blank=True, default='')
    index_label = models.CharField('索引标签', max_length=80, blank=True, default='')
    stat_one_value = models.CharField('统计 1 数值', max_length=40, blank=True, default='')
    stat_one_label = models.CharField('统计 1 标签', max_length=80, blank=True, default='')
    stat_two_value = models.CharField('统计 2 数值', max_length=40, blank=True, default='')
    stat_two_label = models.CharField('统计 2 标签', max_length=80, blank=True, default='')
    empty_text = models.CharField('空状态文案', max_length=160, blank=True, default='')
    filter_aria_label = models.CharField('筛选区辅助标签', max_length=80, blank=True, default='内容分类')
    extra = models.JSONField('页面专属文案 JSON', blank=True, default=dict)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '分区页面'
        verbose_name_plural = '分区页面'
        ordering = ['section']

    def __str__(self):
        return f'{self.get_section_display()} - {self.title}'


class SectionPageTag(models.Model):
    """分区页面标签 chip"""
    section_page = models.ForeignKey(
        SectionPage,
        on_delete=models.CASCADE,
        verbose_name='分区页面',
        related_name='tags',
    )
    name = models.CharField('标签名', max_length=80)
    sort_order = models.PositiveSmallIntegerField('排序', default=0)
    is_visible = models.BooleanField('前台显示', default=True)

    class Meta:
        verbose_name = '分区页面标签'
        verbose_name_plural = '分区页面标签'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class SectionPageFilter(models.Model):
    """分区页面筛选标签页"""
    section_page = models.ForeignKey(
        SectionPage,
        on_delete=models.CASCADE,
        verbose_name='分区页面',
        related_name='filters',
    )
    name = models.CharField('显示名', max_length=80)
    slug = models.SlugField('分类 slug', max_length=80, blank=True, default='')
    sort_order = models.PositiveSmallIntegerField('排序', default=0)
    is_visible = models.BooleanField('前台显示', default=True)

    class Meta:
        verbose_name = '分区页面筛选'
        verbose_name_plural = '分区页面筛选'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Comment(models.Model):
    """评论"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                              verbose_name='文章', related_name='comments')
    nickname = models.CharField('昵称', max_length=50)
    content = models.TextField('评论内容', max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                                null=True, blank=True,
                                verbose_name='父评论', related_name='replies')
    is_approved = models.BooleanField('已审核', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.nickname}: {self.content[:30]}'
