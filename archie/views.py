from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Добро пожаловать на главную страницу!'
        return context
