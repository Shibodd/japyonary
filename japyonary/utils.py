def make_optional_dict(**kwargs):
  return dict((k, v) for k, v in kwargs.items() if v)

def normalize_query(s: str):
  if s is None:
    return None
  s = s.strip()
  if len(s) == 0:
    return None
  return s