from autogen import ConversableAgent
from app import App
from core.capability import Capability
from implementations.faiss_kb import FAISSKnowledgeBase
from implementations.ag2_tools import CurrentDateTimeTool, WeekdayTool, MathTool
from implementations.ag2_tools_manager import AG2ToolsManager
from user_interface.cli import CLI
from user_interface.gui import GUI


default_capabilities: list[Capability] = []


interface = CLI()
# interface = GUI()


app = App(interface, default_capabilities)

# Capabilities
# ============

# add kb
default_capabilities.append(FAISSKnowledgeBase(["pdf", "txt"], 1000, 3))

# add tools manager
tools_manager = AG2ToolsManager(app)
tools_manager.add_tool(CurrentDateTimeTool())
tools_manager.add_tool(WeekdayTool())
tools_manager.add_tool(MathTool())
default_capabilities.append(tools_manager)

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


app.run()
