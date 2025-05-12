from core.capability import Capability


class ErrorHandler(Capability):
    """Handles any errors that may occur during the execution of the agent's tasks."""

    # TODO: supported by Sprint 3
    def __init__(self):
        super().__init__("error_handler")
