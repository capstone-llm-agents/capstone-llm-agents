from autogen import ConversableAgent
from core.chat import Query
from core.model import UnderlyingModel


class AG2Model(UnderlyingModel):
    """A class representing the AG2 model."""

    def __init__(self, ag2_agent: ConversableAgent):
        super().__init__()
        self.ag2_agent = ag2_agent

    def who_asked(self, query: Query) -> ConversableAgent:
        """Get the sender of the query."""
        entity = query.sender

        return ConversableAgent(
            name=entity.name,
            description=entity.description,
        )

    def generate(self, query: Query):
        """Generate a response from the AG2 model."""

        # TODO pass in the sender

        who_asked = self.who_asked(query)

        response = who_asked.initiate_chat(
            recipient=self.ag2_agent,
            message={
                "role": "user",
                "content": query.content,
            },
            max_turns=1,
        )

        return response.summary
