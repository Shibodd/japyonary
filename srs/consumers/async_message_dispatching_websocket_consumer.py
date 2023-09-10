from srs.consumers import AsyncMessageWebsocketConsumer

class AsyncMessageDispatchingWebsocketConsumer(AsyncMessageWebsocketConsumer):
  message_handlers = {}
  async def receive_message(self, message, **payload):
    handler = self.message_handlers.get(message)
    if handler:
      await handler(self, **payload)
    else:
      await self.panic("Unknown message.")