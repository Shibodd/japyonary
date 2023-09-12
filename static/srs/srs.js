var reviewCount = 0;
var server_error = undefined;

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

function on_disconnect(ws, event) {
  console.log('Disconnected!', ws, event);
  if (server_error === undefined) {
    server_error = 'Server disconnected.';
  }
  exit_review();
}

function on_new_card(html, undo_available) {
  console.log("New card!");

  __showAnswer(false);
  document.getElementById("srs-host").innerHTML = html;
  document.getElementById("srs-undo-button").disabled = !undo_available;
}

function answer(confidence) {
  console.log("Answering ", confidence);
  sendMessage('answer', { confidence: confidence });

  reviewCount = reviewCount + 1;
}

function undo() {
  console.log("Undoing");
  sendMessage('undo');

  reviewCount = reviewCount - 1;
}

function showAnswer() {
  console.log("Showing answer");
  __showAnswer(true);
}

function exit_review() {
  console.log("Exiting review...")
  disconnect();
  
  document.querySelector('footer').remove()
  document.getElementById('srs-undo-button', false).remove();
  document.getElementById('srs-exit-button', false).remove();
  document.getElementById('japyonary-button').hidden = false;

  let host = document.getElementById('srs-host');
  host.id = 'srs-results-container';
  host.innerHTML = "Congratulations! You finished " + reviewCount + " reviews.";

  if (server_error) {
    host.innerHTML += '<p class="text-center mt-3"> The server encountered an error: <br/>' + server_error + '</p>';
  }
}

function sendMessage(message, payload) {
  ws.send(JSON.stringify({
    'message': message,
    'payload': payload
  }));
}

function disconnect() {
  ws.onclose = undefined;
  ws.close();
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
  },
  'panic': function(payload) {
    const reason = payload['reason'];
    if (reason !== undefined)
      server_error = reason;
    else
      server_error = "Unknown";
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

window.onbeforeunload = function() {
  disconnect();
};