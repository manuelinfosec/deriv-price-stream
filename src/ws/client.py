import asyncio
from asyncio import Future

from typing import Dict

from shared.utils import generate_random_number
from shared.data_manager import PriceDataManager

from . import handlers
from .base import BaseWebsocketClient


class TradingWebsocketClient(BaseWebsocketClient):
    """
    Application-specific client that maps message topics to handlers
    """

    price_manager: PriceDataManager
    _pending_requests: Dict[int, Future] = {}

    def __init__(self, uri, price_manager):
        super().__init__(uri)

        # The 'dispatcher' maps topics to the functions that handle them
        self._handlers = {"price_tick": handlers.handle_tick_history}

        # Set dispatcher for the base client to use
        self.set_handler_dispatcher(self._dispatch_message)

        # Set the price manager
        self.price_manager = price_manager

    async def _dispatch_message(self, data: dict):
        """
        Intelligently routes messages. It first checks for a specific response
        to a waiting request, and if not found, falls back to general event
        handlers
        """
        # --- Part 1: Logic for Request-Response Pattern ----
        # First check if the message is a direct reply to a waiting function
        req_id = data.get("req_id")

        if req_id and req_id in self._pending_requests:
            # If it is, find the waiting 'Future' and give it the result
            future = self._pending_requests.pop(req_id)
            future.set_result(data)

            # Exit immediately so it doesn't try to find a handler
            return

        # --- Part 2: Existing Logic for Event-Driven Handlers
        # If the message was not a direct reply, proceed to find a handler
        topic = data.get("msg_type")
        handler = self._handlers.get(topic)

        if handler:
            await handler(data, manager=self.price_manager)

        else:
            print(f"Warning: No handler for topic: '{topic}'")

    async def tick_history(self, request_payload: dict):
        """Collect historical candle history"""

        # Create a unique ID  and a future to wait for the results
        request_id = generate_random_number()
        future = asyncio.get_running_loop().create_future()

        # Add the ID to the request and store the future
        request_payload["req_id"] = request_id
        self._pending_requests[request_id] = future

        try:
            # Send the request
            print("Request Payload: ", request_payload)
            await self.send(request_payload)

            # Wait for the listener to receive the matching response
            response = await asyncio.wait_for(future, timeout=30)
            return response
        finally:
            # Clean up in case of timeout or other errors
            self._pending_requests.pop(request_id, None)
