async function ajax_call(url, data) {
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const response = await fetch(
    url,
    {
      method: 'POST',
      mode: 'same-origin', // Do not send CSRF token to another domain.
      headers: {
        'X-CSRFToken': csrftoken,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data)
    }
  );

  if (!response.ok) {
    throw new Error(response);
  }

  const jsonResponse = await response.json();
  if (!jsonResponse.ok) {
    throw new Error(jsonResponse.reason);
  }

  return jsonResponse.payload;
}

async function run_once(lock_obj, fun) {
  try {
    if (lock_obj.__run_once_lock)
      return;
  } catch (e) { }
  
  lock_obj.__run_once_lock = true;
  try {
    await fun();
  } catch (e) {
    console.error(e);
  } finally {
    lock_obj.__run_once_lock = false;
  }
}

function register_button(button, fun) {
  button.addEventListener("click", async function () {
    run_once(button, fun);
  })
}