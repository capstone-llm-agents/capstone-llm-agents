from autogen import ConversableAgent
from core.model import UnderlyingModel


class AG2Model(UnderlyingModel):
    """A class representing the AG2 model."""

    def __init__(self, ag2_agent: ConversableAgent):
        super().__init__()
        self.ag2_agent = ag2_agent

    def generate(self, prompt):
        """Generate a response from the AG2 model."""

        # TODO pass in the sender

        response = self.ag2_agent.initiate_chat(
            recipient=self.ag2_agent,
            message={
                "role": "user",
                "content": prompt,
            },
            max_turns=1,
        )

        return response.summary
