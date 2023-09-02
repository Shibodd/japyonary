import romkan

def build_query(user_query: str):
  user_query = user_query.strip().lower()

  keb = None
  reb = None

  if user_query.startswith('"'):
    keb = user_query
    reb = user_query