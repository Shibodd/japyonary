from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class SrsReviewView(LoginRequiredMixin, TemplateView):
  template_name = 'srs/srs_review.html'