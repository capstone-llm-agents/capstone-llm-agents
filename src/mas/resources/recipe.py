"""Recipe"""
#from app import App

from mas.ag2.ag2_agent import AG2MASAgent
from mas.ag2.ag2_task import AG2Task
from mas.multi_agent_system import MultiAgentSystem
from mas.query.mas_query import MASQuery
from mas.resource_alias import ResourceAlias
from mas.resources.empty import EmptyResource
from mas.task import Task
from mas.recipe_tasks.find_recipe import UserRequestResource, RecipeResource
from utils.string_template import generate_str_using_template


def recipe_agent_mas():
    '''put description here ig'''

    alias = ResourceAlias()

    alias.add_resource_alias("empty", EmptyResource)
    alias.add_resource_alias("recipe", RecipeResource)
    alias.add_resource_alias("topic", UserRequestResource)

    mas = MultiAgentSystem(alias)

    # yaml_file = "./resource/example/example3.yaml"

    mas_query = MASQuery.from_query_string("Generate a recipe name based on user preferences.") # i guess?????

    agent = AG2MASAgent(
        name="RecipeAgent",
        description="You are a recipe generation assistant.",
        #llm_config=app.config_manager.get_llm_config(use_tools=False),
        llm_config={
            "models": [
                {"api_type": "ollama", "model": "gemma3"},
                {"api_type": "ollama", "model": "llama3.2"}
            ],
            "default_model": 0,
            "default_model_with_tools": 1
        },  # Direct config for models
    )

    find_recipe_task = AG2Task(
        name="FindRecipeTask",
        description="Generate a recipe name based on the user's preferences.",
        input_resource=UserRequestResource,
        output_resource=RecipeResource,
        generate_str=generate_str_using_template(
            "Generate a recipe name conforming to the following specifications: '{request}'"
        ),
        agent=agent,
    )

    mas.add_task(find_recipe_task)

    # do a few of these for the tests
    '''Test 1: Reasonable Request'''
    user_request = UserRequestResource(UserRequestResource.UserRequestModel(
        taste="sweet",
        dietary="lactose intolerance",
        ingredients=["strawberry", "chocolate", "egg"],
        time_to_cook=60 #mins
    ))

    output_resources = mas.solve_query(mas_query, {"generate_recipe_name": find_recipe_task}, input_resource=user_request)

    print("Output:")
    for output_resource in output_resources:
        print(output_resource.model.model_dump_json(indent=4, exclude_unset=True))

