from core.capability import Capability


class CommunicationInterface(Capability):
    """An interface for the agent to communicate with other agents or the user."""

    # TODO: supported by Sprint 3
    def __init__(self):
        super().__init__("communication_interface")
