async function heart(deck_id, icon, count) {
  const HEARTED_CLASS = 'bi-heart-fill';
  const UNHEARTED_CLASS = 'bi-heart';

  const was_hearted = icon.classList.contains(HEARTED_CLASS);

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const response = await fetch(
    "ajax/heart_deck",
    {
      method: 'POST',
      mode: 'same-origin', // Do not send CSRF token to another domain.
      headers: {
        'X-CSRFToken': csrftoken,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "deck_id": deck_id,
        "should_heart": !was_hearted
      })
    }
  );
  if (!response.ok) {
    console.log(response);
    return;
  }

  const jsonResponse = await response.json();
  if (!jsonResponse.ok) {
    console.log(jsonResponse);
    return;
  }

  count.innerHTML = jsonResponse.new_heart_count;
  if (jsonResponse.new_hearted) {
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
    
    widget.heart_busy = false;
    button.addEventListener("click", async function () {
      if (widget.heart_busy)
        return;
      
      widget.heart_busy = true;
      try {
        await heart(deck_id, icon, count);
      } finally {
        widget.heart_busy = false;
      }
    })
  }
}
window.addEventListener("load", init);