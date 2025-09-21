from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from typing import override, Any, Coroutine
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.model_providers.openai.call_llm import call_llm_with_messages

class Plan(Action):
    def __init__(self) -> None :
        super().__init__(description="Create a plan")
        self.llm = call_llm_with_messages
    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        actions = context.agent.action_space.get_actions()
        names = []
        for action in actions:
            names.append(action.name)
            names.append(action.description)
        prompt = context.conversation.chat_history.as_dicts() + [
            {
                "role": "system",
                "content": f"You are a professional and meticulous planner. Your task is to create a detailed, step-by-step plan to fulfill the user's request. This plan must be a numbered list of actions to be executed sequentially."
                           f"You must use the following resources in your plan: Actions: {names} and Other Agents: {context.agent.friends}."
                           f"Each step in the plan must be a specific action call or a communication with another agent. Do not include any descriptions of internal thought processes, general assessments, or conversational text. "
                           f"Your final response must contain only the plan itself, without any conversational preambles or explanations."
            }
        ]
        APP_LOGGER.info(prompt)
        plan = await self.llm(prompt)
        context.plan = plan
        APP_LOGGER.debug(plan)
        res = ActionResult()
        res.set_param("response", "")
        return res


