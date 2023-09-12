function showElementById(id, show) {
  let elem = document.getElementById(id);
  if (show)
    elem.classList.remove("d-none");
  else
    elem.classList.add("d-none");
}

function __showAnswer(show) {
  showElementById("srs-answer", show);
  showElementById("srs-shown-answer-buttons", show);
  showElementById("srs-hidden-answer-buttons", !show);
}

function on_connect() {
  console.log('Connected!');
  sendMessage("start_reviews");
}

function on_disconnect() {
  console.log('Disconnected.');
}

function on_new_card(html, undo_available) {
  console.log("New card!", html, undo_available);

  __showAnswer(false);
  document.getElementById("srs-host").innerHTML = html;
  document.getElementById("srs-undo-button").disabled = !undo_available;
}

function answer(confidence) {
  console.log("Answering ", confidence);
  sendMessage('answer', { confidence: confidence });
}

function undo() {
  console.log("Undoing");
  sendMessage('undo');
}

function showAnswer() {
  console.log("Showing answer");
  __showAnswer(true);
}

function sendMessage(message, payload) {
  ws.send(JSON.stringify({
    'message': message,
    'payload': payload
  }));
}

const handlers = {
  'new_card': function(payload) {
    const html = payload['html'];
    const undo_available = payload['undo_available'];
    if (html !== undefined && undo_available !== undefined) {
      on_new_card(html, undo_available);
    } else {
      console.error("Malformed new card!");
    }
  },
  'reviews_done': function(payload) {
    console.log("Reviews done!", payload)
  }
}


var ws = new WebSocket(
  'ws://' + window.location.host + '/ws/'
);

ws.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data.message;
  const payload = data.payload;

  const handler = handlers[message];
  if (handler)
    handler(payload);
  else
    console.error("Unhandled message:", message, payload);
};

ws.onopen = on_connect;
ws.onclose = on_disconnect;