from django.views.generic import TemplateView
from catalog.models import Game


class HomePageView(TemplateView):
    template_name = 'pages/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = Game.objects.order_by('-id')[:5]
        return context
