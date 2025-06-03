from autogen import ConversableAgent
from app import App
from implementations.faiss_kb import FAISSKnowledgeBase

from implementations.communication_interface import SimpleCommunicationInterface


app = App()

# Capabilities
# ============

# kb
app.add_capability(FAISSKnowledgeBase(["pdf", "txt"], 1000, 3))

# communication interface
app.add_capability(SimpleCommunicationInterface())

# Agents
# ======

# add agent
app.add_ag2_agent(
    ConversableAgent(
        name="Assistant",
        system_message="You are a helpful assistant.",
        llm_config=app.config.get_llm_config(),
    ),
)

# evil agent
app.add_ag2_agent(
    ConversableAgent(
        name="Evil Assistant",
        system_message="You are an evil assistant.",
        llm_config=app.config.get_llm_config(),
    ),
)

app.run()
