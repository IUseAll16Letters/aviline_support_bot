from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView

from .utils import pack_log_files_as_html


class LogView(UserPassesTestMixin, TemplateView):
    template_name = 'aviline/log_view.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({'log_file': pack_log_files_as_html()})

        return context_data
