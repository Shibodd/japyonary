function on_new_card(html, undo_available) {
  console.log("New card! ", html, undo_available);
}

const ws = new WebSocket(
  'ws://' + window.location.host + '/ws/'
);

const handlers = {
  'new_card': function(payload) {
    const html = payload['html'];
    const undo_available = payload['undo_available'];
    if (html !== undefined && undo_available !== undefined) {
      on_new_card(html, undo_available);
    } else {
      console.log("Malformed new card!");
    }

  },
  'reviews_done': function(payload) {
    console.log("Reviews done!", payload)
  }
}

ws.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data.message;
  const payload = data.payload;

  const handler = handlers[message];
  if (handler)
    handler(payload);
  else
    console.log("Unhandled message:", message, payload);
};

ws.onopen = function(e) {
  ws.send(JSON.stringify({
    'message': 'start_reviews'
  }));
}

ws.onclose = function(e) {
  // window.location.replace('http://sidanmor.com');
  console.error('Disconnected.');
};