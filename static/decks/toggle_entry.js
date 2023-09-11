// Hearts
async function toggle_entry(deck_id, entry_id, entry, icon) {
  const OWNED_ICON_CLASS = 'bi-dash-circle';
  const UNOWNED_ICON_CLASS = 'bi-plus-circle';

  const new_owned = entry.classList.contains('deck-entry-unowned');
  
  const response = await ajax_call("/decks/ajax/toggle_entry_from_deck", {
    deck_id: deck_id,
    entry_id: entry_id,
    new_owned: new_owned
  });

  if (response.owned != new_owned)
    return;

  if (new_owned) {
    icon.classList.remove(UNOWNED_ICON_CLASS);
    icon.classList.add(OWNED_ICON_CLASS);
    entry.classList.remove('deck-entry-unowned');
  } else {
    icon.classList.remove(OWNED_ICON_CLASS);
    icon.classList.add(UNOWNED_ICON_CLASS);
    entry.classList.add('deck-entry-unowned');
  }
}

function init() {
  const deck_id = document.querySelector('[name=japyonary-deck-id]').value;
  const entries = document.getElementsByClassName("deck-entry");

  for (let i = 0; i < entries.length; ++i) {
    const entry = entries[i];

    const button = entry.querySelector('button.add-entry-to-deck-btn');
    const entry_id = entry.getAttribute('data-id');
    const icon = button.querySelector('i');
    register_button(button, async function() {
      await toggle_entry(deck_id, entry_id, entry, icon);
    });
  }
}

document.addEventListener("DOMContentLoaded", init);