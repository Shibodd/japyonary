import romkan
import itertools
import re
from . import models

__HIRAGANA = set(itertools.chain.from_iterable(romkan.KANROM_H.keys()))
__KATAKANA = set(itertools.chain.from_iterable(romkan.KANROM.keys()))
__KANA = __HIRAGANA.union(__KATAKANA)

is_english = re.compile('^[A-Za-z\d\s]*$')

def build_query(user_query: str):
  user_query = user_query.strip().lower()
  hep = romkan.to_hepburn(user_query)
  lookup_meaning = is_english.match(user_query) is not None

  