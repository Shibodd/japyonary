from dictionary.models import Entry
from japyonary import utils
from srs.models import Flashcard
from django.contrib.auth.decorators import login_required

@login_required
def add_remove_entry_in_srs(request):
  data = utils.parse_ajax_request(request)
  utils.assert_ajax_data_has_fields(data, 'entry_id', 'should_add')

  entry = Entry.objects.filter(pk=data['entry_id']).first()
  if entry is None:
    return utils.make_ajax_response_bad('Entry does not exist')
  
  flashcard = Flashcard.objects.filter(owner=request.user, entry_id=data['entry_id']).first()
  doesnt_exist = flashcard is None

  if data['should_add'] == doesnt_exist:
    if doesnt_exist:
      Flashcard.objects.create(owner = request.user, entry = entry)
    else:
      # TODO: Need to do this properly, but i'm out of time
      return utils.make_ajax_response_bad('NOT IMPLEMENTED')
  
  return utils.make_ajax_response_ok(new_added = data['should_add'])