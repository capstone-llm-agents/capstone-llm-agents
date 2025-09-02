"""Some dummy actions for testing purposes."""

from llm_mas.action_system.core.action import Action

SOLVE_MATH = Action(
    name="SolveMath",
    description="Solves math equations easily.",
)

GET_CURRENT_DATE = Action(
    name="GetCurrentDate",
    description="Retrieves the current date and time.",
)

GET_WEATHER = Action(
    name="GetWeather",
    description="Retrieves the current weather for a specified location.",
)

GET_CURRENT_TIME = Action(
    name="GetCurrentTime",
    description="Retrieves the current time.",
)

GET_RANDOM_NUMBER = Action(
    name="GetRandomNumber",
    description="Generates a random number within a specified range.",
)

GET_WEB_RESULT = Action(
    name="Get web result",
    description="Return a response from a websearch.",
)
# is this being used??