from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AboutPageView, SectionPageView, PostViewSet, CategoryViewSet, TagViewSet, MediaImageViewSet

app_name = 'blog'

# DRF Router 自动注册 URL
router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'images', MediaImageViewSet)

urlpatterns = [
    path('about/', AboutPageView.as_view(), name='about-page'),
    path('section-pages/<str:section>/', SectionPageView.as_view(), name='section-page'),
    path('', include(router.urls)),
]
