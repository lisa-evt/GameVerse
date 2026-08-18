from django.urls import path

from .views import HomePageView, AboutPageView, RoadmapPageView


urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('roadmap/', RoadmapPageView.as_view(), name='roadmap'),
]