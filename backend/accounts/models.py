from django.db import models


class Profile(models.Model):
    """站长信息"""
    nickname = models.CharField('昵称', max_length=50)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True)
    bio = models.TextField('个人简介', max_length=500, blank=True, default='')
    slogan = models.CharField('首页Slogan', max_length=200, blank=True,
                               default='在暗处寻找光')
    social_links = models.JSONField('社交链接', default=dict, blank=True,
                                     help_text='JSON 格式: {"github": "url", "bilibili": "url"}')

    class Meta:
        verbose_name = '站长信息'
        verbose_name_plural = '站长信息'

    def __str__(self):
        return self.nickname
