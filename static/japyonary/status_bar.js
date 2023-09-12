let status_bar_timeout_id = undefined;

function trigger_status_bar(message, ok) {
  let elem = document.getElementById("status-bar");

  elem.style.opacity = 1;
  elem.style.background = ok? "rgba(0, 255, 0, 0.3)" : "rgba(255, 0, 0, 0.3)";
  elem.innerHTML = message;

  if (status_bar_timeout_id !== undefined)
    clearTimeout(status_bar_timeout_id);
  
  status_bar_timeout_id = setTimeout(function () {
    elem.style.opacity = 0;
  }, 3000);
}