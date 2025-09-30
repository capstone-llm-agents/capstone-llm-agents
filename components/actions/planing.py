import json
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from typing import override, Coroutine
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.model_providers.openai.call_llm import call_llm_with_messages
from typing_extensions import List, Any
from components.actions.simple_response import SimpleResponse

async def plan_router(prompt: str, actions: List[Any], Agents: List[Any]):
    llm = call_llm_with_messages

    llm_prompt = (f'''You are the "Router" for an AI agent. Your job is to analyze the user's request and determine the most appropriate strategy for handling it. You must choose one of the following three strategies. *IMPORTANT Respond with ONLY a single JSON object representing your choice and do not include ```json in your response.
                    
                    1.  `direct_answer`: Choose this if the request is a simple conversational question, a greeting, or something that doesn't require any external tools (e.g., "Hello", "How are you?", "Thank you").
                    2.  `single_action`: Choose this if the request can be fully answered by using one and only one of the available tools. Your response must specify the tool name and its arguments.
                    3.  `generate_plan`: Choose this if the request is complex and requires multiple tool calls, conditional logic, or synthesizing information from different sources.
                    4. For single_action your response should be like the following:
                    {{
                      "steps": [
                        {{
                          "actions": "action_name",
                          "arguments": {{"anyarguments, e.g agent_name, query"}}
                        }},
                      ]
                    }}
                    Here are the available tools:
                    Actions:{actions}
                    These are the other agents you can contact using the AskFriendForHelp tool:
                    Agents:{Agents}
                    User Request: {prompt}
                        ''')
    llm_prompt_update = [{"role": "system", "content": f"{llm_prompt}"}]
    plan =  await llm(llm_prompt_update)
    APP_LOGGER.debug(f"plan as json{plan}")
    plan_dict = json.loads(plan)
    APP_LOGGER.debug(f'Plan router tool plan: {plan_dict}')
    return plan_dict


class Plan(Action):
    def __init__(self) -> None :
        super().__init__(description="Create a plan")
        self.llm = call_llm_with_messages
    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:

        #setup variables such as the actions, friends, messages and user prompt ready for the llm
        actions = context.agent.action_space.get_actions()
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        friends = []
        action_name = []

        #setup params extract the information out of context params and format it in a presentable way for the llm
        for action in actions:
            if action.description == "Stops the agent's execution":
                continue
            else:
                action_name.append(action.name)
                action_name.append(action.description)

        for friend in context.agent.friends:
            friends.append(friend.name)
            friends.append(friend.description)

        result = await plan_router(prompt=messages[-1],actions=action_name, Agents=friends)
        APP_LOGGER.info(f"This is the plan as a dict: {result}")


        if result['steps']:
            APP_LOGGER.info(f"single_action")
            context.plan = result
            res = ActionResult()
            res.set_param("response", "")
            return res
        elif result['strategy'] == 'direct_answer':
            APP_LOGGER.info(f"direct_answer")
            context.plan = f"Use {SimpleResponse.__name__}"
            res = ActionResult()
            res.set_param("response", "")
            return res
        elif result['strategy'] == "generate_plan":
            APP_LOGGER.info(f"generate_plan")
            prompt = [{"role": "user", "content": f"{messages[-1]}"}] + [
                {
                    "role": "system",
                    "content": f"""
                    You are a meticulous planner AI. Your task is to create a detailed, step-by-step plan to fulfill the user's request. 
                    

                    The plan must be a JSON object containing a list of steps. Each step must be an object with a "actions" and "arguments".
                    Do not include ```json in your response. 
                    And should be in the following format:
                             {{
                              "steps": [
                                {{
                                  "actions": "action_name",
                                  "arguments": {{"anyarguments, e.g agent_name, query"}}
                                }},
                              ]
                            }}
                    You have access to the following resources:
                    - Actions: {action_name}
                    - Other Agents: {friends}

                    Carefully analyze the user's request and the available actions.

                    If the request is impossible to fulfill with the available actions, your plan should consist of a single step using the tool '{SimpleResponse.__name__}'.
                   
                    *IMPORTANT Your final output must be only the JSON plan object not any informative information."""
                }
            ]
            plan = await self.llm(prompt)
            APP_LOGGER.debug(f"plan: {plan}")
            plan_as_dict = json.loads(plan)
            for step in plan_as_dict['steps']:
                step['Completed'] = False
            context.plan = plan_as_dict
            APP_LOGGER.debug(f"plan as a dict {plan_as_dict}")
            res = ActionResult()
            res.set_param("response", "")
            return res
        else:
            res = ActionResult()
            res.set_param("response", "")
            return res







