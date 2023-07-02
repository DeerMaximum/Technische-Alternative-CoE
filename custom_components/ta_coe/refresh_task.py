"""CoE server value refresh task."""
import asyncio
from contextlib import suppress

from .const import _LOGGER
from .state_sender import StateSender


class RefreshTask:
    """Handle the refresh of values to the CoE server."""

    def __init__(self, sender: StateSender):
        """Initialize."""
        self._sender = sender
        self.is_started = False
        self._task = None

    async def start(self):
        """Start the task."""
        _LOGGER.debug("Try to start refresh task")
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        """Stop the task."""
        _LOGGER.debug("Try to stop refresh task")
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        """Run action."""
        _LOGGER.info("Refresh task started")
        while True:
            await asyncio.sleep(10 * 60)
            await self._sender.update()
