from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = 'pages/index.html'


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RoadmapPageView(TemplateView):
    template_name = 'pages/roadmap.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403.html', status=403)


def server_error(request):
    return render(request, 'pages/500.html', status=500)

def bad_request(request, exception):
    return render(request, 'pages/400.html', status=400)