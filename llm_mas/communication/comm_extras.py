"""Reason for various message types."""


class Reason:
    """A reason for rejection or disappointment."""

    def __init__(self, text: str) -> None:
        """Initialize the reason with text."""
        self.text = text

    def __str__(self) -> str:
        """Return the reason as a string."""
        return self.text


class CommError:
    """An error that occurred during communication."""

    def __init__(self, text: str) -> None:
        """Initialize the error with text."""
        self.text = text

    def __str__(self) -> str:
        """Return the error as a string."""
        return self.text
