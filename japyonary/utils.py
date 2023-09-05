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