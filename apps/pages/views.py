from django.views.generic import TemplateView

from apps.catalog.models import Game


class HomePageView(TemplateView):
    template_name = 'pages/index.html'


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RoadmapPageView(TemplateView):
    template_name = 'pages/roadmap.html'
