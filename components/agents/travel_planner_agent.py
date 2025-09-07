"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.book_accomodation import BookAccommodation
from components.actions.book_flight import BookFlight
from components.actions.create_itinerary import CreateItinerary
from components.actions.estimate_budget import EstimateBudget
from components.actions.get_trip_details import GetTripDetails
from components.actions.search_accomodations import SearchAccommodations
from components.actions.search_activities import SearchActivities
from components.actions.search_flights import SearchFlights
from components.actions.travel_narrower import TravelNarrower
from components.actions.travel_response import TravelResponse
from components.actions.websearch import WebSearch
from components.actions.memory import MemorySearchlong, MemorySavelong
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import get_embedding
from llm_mas.model_providers.ollama.call_llm import call_llm as ollamaAI
from llm_mas.model_providers.openai.call_llm import call_llm as gptAI
from llm_mas.tools.tool_action_creator import DefaultToolActionCreator
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower

action_space = ActionSpace()
narrower = TravelNarrower()
selector = EmbeddingSelector(get_embedding)

# tools
tool_narrower = DefaultToolNarrower()
tool_creator = DefaultToolActionCreator()
tool_manager = ToolManager(
    tool_narrower,
)

TRAVEL_PLANNER_AGENT = Agent(
    "TravelAgent",
    "A travel planning assistant that helps users plan and book their trips.",
    action_space,
    narrower,
    selector,
    tool_manager,
)


# add some actions
TRAVEL_PLANNER_AGENT.add_action(BookAccommodation())
TRAVEL_PLANNER_AGENT.add_action(BookFlight())
TRAVEL_PLANNER_AGENT.add_action(CreateItinerary())
TRAVEL_PLANNER_AGENT.add_action(EstimateBudget())
TRAVEL_PLANNER_AGENT.add_action(WebSearch())
TRAVEL_PLANNER_AGENT.add_action(MemorySearchlong())
TRAVEL_PLANNER_AGENT.add_action(SearchFlights())
TRAVEL_PLANNER_AGENT.add_action(SearchAccommodations())
TRAVEL_PLANNER_AGENT.add_action(SearchActivities())
TRAVEL_PLANNER_AGENT.add_action(SimpleResponse())
TRAVEL_PLANNER_AGENT.add_action(TravelResponse())
TRAVEL_PLANNER_AGENT.add_action(GetTripDetails())
TRAVEL_PLANNER_AGENT.add_action(StopAction())
TRAVEL_PLANNER_AGENT.add_action(MemorySavelong())
# add edges
narrower.add_action_edge(EstimateBudget(), [MemorySearchlong()])
narrower.add_action_edge(SearchFlights(), [BookFlight(), MemorySearchlong()])
narrower.add_action_edge(BookFlight(), [MemorySearchlong(), MemorySavelong()])
narrower.add_action_edge(SearchAccommodations(), [BookAccommodation(), MemorySearchlong()])
narrower.add_action_edge(BookAccommodation(), [ MemorySearchlong()])
narrower.add_action_edge(SearchActivities(), [ MemorySearchlong(), MemorySavelong()])
narrower.add_action_edge(CreateItinerary(), [MemorySearchlong(), MemorySavelong() ])
narrower.add_action_edge(TravelResponse(), [StopAction()])
narrower.add_action_edge(WebSearch(), [MemorySavelong()])
narrower.add_action_edge(GetTripDetails(), [MemorySearchlong()])
narrower.add_action_edge(MemorySearchlong(), [SimpleResponse(), TravelResponse()])
narrower.add_action_edge(SimpleResponse(), [StopAction()])
narrower.add_action_edge(MemorySavelong(), [SimpleResponse(), TravelResponse()])
# default action
narrower.add_default_action(GetTripDetails())
narrower.add_default_action(SearchFlights())
narrower.add_default_action(SearchAccommodations())
narrower.add_default_action(EstimateBudget())
narrower.add_default_action(SearchActivities())
narrower.add_default_action(TravelResponse())
narrower.add_default_action(CreateItinerary())
narrower.add_default_action(WebSearch())
