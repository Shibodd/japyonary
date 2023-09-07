// Hearts
async function heart(deck_id, icon, count) {
  const HEARTED_CLASS = 'bi-heart-fill';
  const UNHEARTED_CLASS = 'bi-heart';

  const was_hearted = icon.classList.contains(HEARTED_CLASS);

  const response = await ajax_call("/decks/ajax/heart_deck", {
    "deck_id": deck_id,
    "should_heart": !was_hearted
  });

  count.innerHTML = response.new_heart_count;
  if (response.new_hearted) {
    icon.classList.add(HEARTED_CLASS);
    icon.classList.remove(UNHEARTED_CLASS);
  } else {
    icon.classList.add(UNHEARTED_CLASS);
    icon.classList.remove(HEARTED_CLASS);
  }
}

function init() {
  const heart_widgets = document.getElementsByClassName("heart-widget");

  for (let i = 0; i < heart_widgets.length; ++i) {
    const widget = heart_widgets[i];

    const deck_id = widget.getAttribute("data-id");
    const count = widget.querySelector('span');
    const button = widget.querySelector('button');
    const icon = widget.querySelector('i');
    register_button(button, async function() {
      await heart(deck_id, icon, count);
    });
  }
}

document.addEventListener("DOMContentLoaded", init);