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
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.selectors.llm_selector import LLMSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import call_llm
from llm_mas.tools.tool_action_creator import DefaultToolActionCreator
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower

action_space = ActionSpace()
narrower = TravelNarrower()
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
TRAVEL_PLANNER_AGENT.add_action(WebSearch())

TRAVEL_PLANNER_AGENT.add_action(SearchFlights())
TRAVEL_PLANNER_AGENT.add_action(SearchAccommodations())
TRAVEL_PLANNER_AGENT.add_action(SearchActivities())

TRAVEL_PLANNER_AGENT.add_action(TravelResponse())
TRAVEL_PLANNER_AGENT.add_action(GetTripDetails())
TRAVEL_PLANNER_AGENT.add_action(StopAction())

# add edges
narrower.add_action_edge(EstimateBudget(), [TravelResponse()])
narrower.add_action_edge(SearchFlights(), [BookFlight()])
narrower.add_action_edge(BookFlight(), [TravelResponse()])
narrower.add_action_edge(SearchAccommodations(), [BookAccommodation()])
narrower.add_action_edge(BookAccommodation(), [TravelResponse()])
narrower.add_action_edge(SearchActivities(), [TravelResponse()])
narrower.add_action_edge(CreateItinerary(), [EstimateBudget()])
narrower.add_action_edge(TravelResponse(), [StopAction()])
narrower.add_action_edge(WebSearch(), [TravelResponse()])

narrower.add_action_edge(GetTripDetails(), [TravelResponse()])

# default action
narrower.add_default_action(GetTripDetails())
narrower.add_default_action(SearchFlights())
narrower.add_default_action(SearchAccommodations())
narrower.add_default_action(EstimateBudget())
narrower.add_default_action(SearchActivities())
narrower.add_default_action(TravelResponse())
narrower.add_default_action(CreateItinerary())
narrower.add_default_action(WebSearch())

# word filters
narrower.add_default_filter(
    SearchFlights(),
    ["flight", "flights", "airline", "airlines", "book flight", "book flights", "search flight", "search flights"],
)
narrower.add_default_filter(
    SearchAccommodations(),
    [
        "accommodation",
        "accommodations",
        "hotel",
        "hotels",
        "book accommodation",
        "book accommodations",
        "search accommodation",
        "search accommodations",
    ],
)
narrower.add_default_filter(
    SearchActivities(),
    [
        "activity",
        "activities",
        "tour",
        "tours",
        "book activity",
        "book activities",
        "search activity",
        "search activities",
    ],
)
narrower.add_default_filter(
    EstimateBudget(),
    [
        "budget",
        "cost",
        "price",
        "estimate budget",
        "estimate cost",
        "estimate price",
        "calculate budget",
        "calculate cost",
        "calculate price",
    ],
)
narrower.add_default_filter(
    CreateItinerary(),
    [
        "itinerary",
        "plan",
        "planning",
        "create itinerary",
        "create plan",
        "create planning",
        "make itinerary",
        "make plan",
        "make planning",
    ],
)
narrower.add_default_filter(
    GetTripDetails(),
    [
        "trip details",
        "get trip details",
        "trip information",
        "get trip information",
        "trip data",
        "get trip data",
    ],
)

narrower.add_default_filter(
    WebSearch(),
    [
        "web search",
        "search the web",
        "search online",
        "find information",
        "look up",
        "search for",
        "find",
        "search",
        "look for",
    ],
)
