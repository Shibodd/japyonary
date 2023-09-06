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