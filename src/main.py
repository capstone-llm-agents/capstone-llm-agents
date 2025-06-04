from autogen import ConversableAgent
from app import App
from implementations.faiss_kb import FAISSKnowledgeBase

from implementations.communication_interface import SimpleCommunicationInterface
from implementations.ag2_tools import CurrentDateTimeTool, WeekdayTool, MathTool
from implementations.ag2_tools_manager import AG2ToolsManager


app = App()

# Capabilities
# ============

# kb
app.add_capability(FAISSKnowledgeBase(["pdf", "txt"], 1000, 3))

# communication interface
app.add_capability(SimpleCommunicationInterface())

# add tools manager
tools_manager = AG2ToolsManager(app)
tools_manager.add_tool(CurrentDateTimeTool())
tools_manager.add_tool(WeekdayTool())
tools_manager.add_tool(MathTool())

app.add_capability(tools_manager)

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
