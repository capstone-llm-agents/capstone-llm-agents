"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.book_accomodation import BookAccommodation
from components.actions.book_flight import BookFlight
from components.actions.create_itinerary import CreateItinerary
from components.actions.estimate_budget import EstimateBudget
from components.actions.get_trip_details import GetTripDetails
from components.actions.search_accomodations import SearchAccommodations
from components.actions.search_activities import SearchActivities
from components.actions.search_flights import SearchFlights
from components.actions.travel_response import TravelResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.llm_selector import LLMSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import call_llm
from llm_mas.tools.tool_action_creator import DefaultToolActionCreator
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = LLMSelector(call_llm)

# tools
tool_narrower = DefaultToolNarrower()
tool_creator = DefaultToolActionCreator()
tool_manager = ToolManager(
    tool_narrower,
)

TRAVEL_PLANNER_AGENT = Agent("Travel Agent", action_space, narrower, selector, tool_manager)


# add some actions
TRAVEL_PLANNER_AGENT.add_action(BookAccommodation())
TRAVEL_PLANNER_AGENT.add_action(BookFlight())
TRAVEL_PLANNER_AGENT.add_action(CreateItinerary())
TRAVEL_PLANNER_AGENT.add_action(EstimateBudget())

TRAVEL_PLANNER_AGENT.add_action(SearchFlights())
TRAVEL_PLANNER_AGENT.add_action(SearchAccommodations())
TRAVEL_PLANNER_AGENT.add_action(SearchActivities())

TRAVEL_PLANNER_AGENT.add_action(TravelResponse())
TRAVEL_PLANNER_AGENT.add_action(GetTripDetails())
TRAVEL_PLANNER_AGENT.add_action(StopAction())

# add edges
narrower.add_action_edge(EstimateBudget(), [SearchFlights(), SearchAccommodations(), SearchActivities()])
narrower.add_action_edge(SearchFlights(), [BookFlight()])
narrower.add_action_edge(BookFlight(), [TravelResponse()])
narrower.add_action_edge(SearchAccommodations(), [BookAccommodation()])
narrower.add_action_edge(BookAccommodation(), [TravelResponse()])
narrower.add_action_edge(SearchActivities(), [TravelResponse()])
narrower.add_action_edge(CreateItinerary(), [EstimateBudget()])
narrower.add_action_edge(TravelResponse(), [StopAction()])

narrower.add_action_edge(GetTripDetails(), [TravelResponse()])

# default action
narrower.add_default_action(GetTripDetails())
narrower.add_default_action(SearchFlights())
narrower.add_default_action(SearchAccommodations())
