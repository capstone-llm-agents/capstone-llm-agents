"""Some dummy actions for testing purposes."""

from llm_mas.action_system.core.action import Action

SOLVE_MATH = Action(
    name="Solve Math",
    description="Solves math equations easily.",
)

GET_CURRENT_DATE = Action(
    name="Get Current Date",
    description="Retrieves the current date and time.",
)

GET_WEATHER = Action(
    name="Get Weather",
    description="Retrieves the current weather for a specified location.",
)

GET_CURRENT_TIME = Action(
    name="Get Current Time",
    description="Retrieves the current time.",
)

GET_RANDOM_NUMBER = Action(
    name="Get Random Number",
    description="Generates a random number within a specified range.",
)
