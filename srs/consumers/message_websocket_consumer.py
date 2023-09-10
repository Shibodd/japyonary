from channels.generic.websocket import AsyncJsonWebsocketConsumer

class MessageWebsocketConsumer(AsyncJsonWebsocketConsumer):
  message_handlers = {}

  async def send_message(self, message, **kwargs):
    await self.send_json({
      'message': message,
      'payload': kwargs
    })

  async def panic(self, reason, code = None):
    await self.send_message('panic', reason=reason)
    await self.close(code)

  async def receive_json(self, content, **kwargs):
    """ Dispatches the message to the designated message handler. """

    handler = self.message_handlers.get(content.get('message'))
    if handler:
      await handler(self, content.get('payload'))
    else:
      await self.panic('Unknown message')