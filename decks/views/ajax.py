from japyonary import utils
from django.contrib.auth.decorators import login_required
from decks.models import Deck
from dictionary.models import Entry
from django import http
from django.core.exceptions import BadRequest


@login_required
def heart_deck(request):
  data = utils.parse_ajax_request(request)
  utils.assert_ajax_data_has_fields(data, 'deck_id', 'should_heart')

  try:
    deck = Deck.objects.get(pk=data['deck_id'])
  except Deck.DoesNotExist:
    return utils.make_ajax_response_bad('Deck does not exist')

  if deck.owner == request.user:
    return utils.make_ajax_response_bad('Cannot like own deck')
  
  new_hearted = not deck.hearts.contains(request.user)
  if data['should_heart'] == new_hearted:
    if new_hearted:
      deck.hearts.add(request.user)
    else:
      deck.hearts.remove(request.user)
  
  return utils.make_ajax_response_ok(
    new_hearted = new_hearted,
    new_heart_count = deck.hearts.count()
  )

@login_required
def toggle_entry_from_deck(request: http.HttpRequest):
  data = utils.parse_ajax_request(request)
  utils.assert_ajax_data_has_fields(data, 'entry_id', 'deck_id', 'new_owned')

  if not isinstance(data['new_owned'], bool):
    raise BadRequest('Invalid request')

  try:
    deck = Deck.objects.get(pk=data['deck_id'])
  except Deck.DoesNotExist:
    return utils.make_ajax_response_bad('Deck does not exist')
  
  if deck.owner != request.user:
    return utils.make_ajax_response_bad("Cannot edit entries of another user's deck")
  
  entry = Entry.objects.filter(pk = data['entry_id']).first()
  if entry is None:
    return utils.make_ajax_response_bad('Entry does not exist.')
  
  if data['new_owned']:
    deck.dictionary_entries.add(entry)
  else:
    deck.dictionary_entries.remove(entry)

  return utils.make_ajax_response_ok(owned=data['new_owned'])