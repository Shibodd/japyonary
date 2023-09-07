import io
import sudachipy.dictionary
from django.core.files.uploadedfile import UploadedFile
import itertools
from dictionary.models import KEle

def __tokenize_text(file: io.TextIOBase,
    sudachi_dict_type = 'full', 
    sudachi_split_mode = sudachipy.SplitMode.B):
  
  lines = (l.strip() for l in file)
  lines = (l for l in lines if len(l) > 0)

  # TODO: Maybe avoiding to load sudachipy's dictionary at every request is not a bad idea, no?
  tokenizer_obj = sudachipy.dictionary.Dictionary(dict_type=sudachi_dict_type).create(mode=sudachi_split_mode)
  return itertools.chain.from_iterable(tokenizer_obj.tokenize(line) for line in lines)

# Ignore everything that is not a noun, verb or adjective.
# Don't bother querying the DB as sudachipy has an internal dictionary.
__WHITELIST_POS = ['名詞', '動詞', '形容']
__BLACKLIST_POS = ['数詞']
def __filter_tokens(tokens):
  def tok_fil(tok):
    poses = tok.part_of_speech()
    return any(pos[:2] in __WHITELIST_POS for pos in poses) \
       and all(pos[:2] not in __BLACKLIST_POS for pos in poses)

  return filter(tok_fil, tokens)

def get_entries_from_file(file: UploadedFile):
  tokens = __filter_tokens(__tokenize_text(io.TextIOWrapper(file, encoding='utf8')))
  tokens = itertools.islice(tokens, 50000)

  # Read and close
  words = set(tok.dictionary_form() for tok in tokens)
  file.close()

  # Now we have to match the word set with our dictionary entries.
  # TODO: CPU goes BRRR, maybe cache this
  lookup = dict((dbobj['keb'], dbobj['entry_id']) for dbobj in KEle.objects.values('entry_id', 'keb'))
  return filter(None, (lookup.get(word) for word in words))
