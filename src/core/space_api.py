from core.chat import ChatHistory
from core.mas import MAS
from core.space import Space


class SpaceAPI:
    """API layer for accessing the differente spaces in the MAS."""

    def __init__(self, spaces: list[Space], mas: MAS):
        self.spaces = spaces
        self.mas = mas

    # TODO: remove this just for testing purposes
    def add_space(self, space: Space) -> None:
        """Add a new space to the MAS."""
        self.spaces.append(space)

    # TODO: remove this just for testing purposes
    def remove_space(self, space: Space) -> None:
        """Remove a space from the MAS."""
        if space in self.spaces:
            self.spaces.remove(space)
        else:
            raise ValueError("Space not found in MAS.")

    def get_spaces(self) -> list[Space]:
        """Get all spaces in the MAS."""
        return self.spaces

    def get_chat_history_for_space(self, space: Space) -> ChatHistory:
        """Get the chat history for a specific space."""
        return space.get_chat_history()
