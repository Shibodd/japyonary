from channels.generic.websocket import AsyncJsonWebsocketConsumer

class AsyncMessageWebsocketConsumer(AsyncJsonWebsocketConsumer):
  # Tx
  async def send_message(self, message, **payload):
    await self.send_json({
      'message': message,
      'payload': payload
    })

  async def panic(self, reason, code = None):
    await self.send_message('panic', reason=reason)
    await self.close(code)

  # Rx
  async def receive_message(self, message, **payload):
    pass
  
  async def receive_json(self, content, **kwargs):
    message = content.get('message')
    payload = content.get('payload', {})

    if not isinstance(message, str):
      await self.panic('Protocol error')
    
    await self.receive_message(message, **payload)