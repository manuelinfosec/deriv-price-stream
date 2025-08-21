import asyncio
import json
from asyncio import Task


import websockets


class BaseWebsocketClient:
    """Handles the low-level WebSocket connection and message loop"""
    _listener_task: Task | None = None

    def __init__(self, uri):
        self._uri = uri
        self._connection = None
        self._handler_dispatcher = None

    async def connect(self):
        """Establishes the Websocket connection"""
        try:
            self._connection = await websockets.connect(self._uri)
            print("\n🔗 Websocket connection established with broker.")
            # Start the listener loop as a concurrent task
            self._listener_task = asyncio.create_task(self._listen())
        except (websockets.exceptions.ConnectionClosedError, OSError) as e:
            print(f"❌ Connection failed: {e}. Retrying...")
            await asyncio.sleep(5)
            await self.connect()

    def set_handler_dispatcher(self, dispatcher):
        """Sets the dispathcer function that will process messaages."""
        self._handler_dispatcher = dispatcher

    async def _listen(self):
        """Listens for incomming messages and passes them to the dispatcher"""
        while True:
            try:
                message = await self._connection.recv()
                if self._handler_dispatcher:
                    data = json.loads(message)
                    # Let the dispatcher handle the data
                    await self._handler_dispatcher(data)
            except websockets.exceptions.ConnectionClosedError:
                print("Connection lost. Reconnecting...")
                await self.connect()
                break  # Exit this loop, a new one start on reconnect

    async def send(self, message: dict):
        """Sends a JSON message to the server"""
        if self._connection:
            await self._connection.send(json.dumps(message))
            # print("Sent message", message)

    async def close(self):
        """Closes the Websocket connection"""
        # Destroy the `listen()` task
        if self._listener_task:
            self._listener_task.cancel()
        if self._connection:
            await self._connection.close()
            print("Websoocket connection closed")
