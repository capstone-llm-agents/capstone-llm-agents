"""Produces a random ID string."""

import random


def generate_random_id(length: int = 6) -> str:
    """Generate a random ID string of given length."""
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=length))  # noqa: S311
