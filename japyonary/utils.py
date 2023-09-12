import more_itertools
from django.contrib import messages

def make_optional_dict(**kwargs):
  return dict((k, v) for k, v in kwargs.items() if v)

def normalize_query(s: str):
  if s is None:
    return None
  s = s.strip()
  if len(s) == 0:
    return None
  return s

import django.contrib.auth.decorators
@django.contrib.auth.decorators.login_required
def login_required_test(request):
  """ Returns an HTTPResponse if the login_required test fails. Otherwise, it returns None."""
  return None

def user_passes_test(fun):
  @django.contrib.auth.decorators.user_passes_test(fun)
  def test(request):
    return None
  return test

import json
from django.http import JsonResponse
from django.core.exceptions import BadRequest

def parse_ajax_request(request):
  if request.method != 'POST':
    raise BadRequest('Invalid request')
  
  ans = json.load(request)
  return ans

def assert_ajax_data_has_fields(dict, *keys):
  if any(k not in dict for k in keys):
    raise BadRequest('Malformed request')

def make_ajax_response_ok(**payload):
  return JsonResponse({
    'ok': True,
    'payload': payload
  })

def make_ajax_response_bad(reason):
  return JsonResponse({
    'ok': False,
    'reason': reason
  })



def add_statusbar_message(request, message, ok=True):
  messages.add_message(request, messages.INFO if ok else messages.ERROR, message, fail_silently=False)

class StatusBarFormValidationMixin():
  status_bar_message_on_success = "Success"
  status_bar_message_on_fail = "Operation failed"

  def form_valid(self, form):
    ans = super().form_valid(form)
    add_statusbar_message(self.request, self.status_bar_message_on_success, True)
    return ans
  
  def form_invalid(self, form):
    add_statusbar_message(self.request, self.status_bar_message_on_fail, False)
    ans = super().form_invalid(form)
    return ans
  

def load_statusbar_context(ctx, request):
  message = more_itertools.last(messages.get_messages(request), None)
  if message is not None:
    ctx['status_bar_message'] = message.message
    ctx['status_bar_ok'] = "true" if message.level != messages.ERROR else "false"

class StatusBarContextMixin():
  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    load_statusbar_context(ctx, self.request)
    return ctx