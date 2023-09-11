// Hearts
async function add_flashcard(entry_id, button) {
  const response = await ajax_call("/srs/ajax/add_flashcard", { entry_id: entry_id, should_add: true });

  if (response.new_added) {
    console.log("Succesfully added flashcard");
    button.disabled = true;
  } else {
    console.log("Flashcard addition failed");
  }
}

function init() {
  const entries = document.getElementsByClassName("dictionary-entry");
  console.log("init");
  for (let i = 0; i < entries.length; ++i) {
    const entry = entries[i];

    const button = entry.querySelector('button.add-flashcard-btn');
    const entry_id = entry.getAttribute('data-id');
    register_button(button, async function() {
      await add_flashcard(entry_id, button);
    });
  }
}

document.addEventListener("DOMContentLoaded", init);