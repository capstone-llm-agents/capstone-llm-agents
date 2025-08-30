"""The background tasks utility module."""

import asyncio
import weakref

BACKGROUND_TASKS: weakref.WeakSet[asyncio.Task] = weakref.WeakSet()
