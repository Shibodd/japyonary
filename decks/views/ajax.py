import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from decks.models import Deck
@login_required
def heart_deck(request):
  if request.method != 'POST':
    return HttpResponseBadRequest('Invalid request')
  
  data = json.load(request)
  deck_id = data.get('deck_id')
  should_heart = data.get('should_heart')

  if deck_id is None or should_heart is None:
    return HttpResponseBadRequest('Invalid request')

  try:
    deck = Deck.objects.get(pk=deck_id)
  except Deck.DoesNotExist:
    return JsonResponse({
      'ok': False,
      'reason': 'Deck does not exist'
    })

  if deck.owner == request.user:
    return JsonResponse({
      'ok': False,
      'reason': 'Cannot like own deck'
    })
  
  new_hearted = not deck.hearts.contains(request.user)
  if should_heart == new_hearted:
    if new_hearted:
      deck.hearts.add(request.user)
    else:
      deck.hearts.remove(request.user)
  
  return JsonResponse({
    'ok': True,
    'new_hearted': new_hearted,
    'new_heart_count': deck.hearts.count()
  })
