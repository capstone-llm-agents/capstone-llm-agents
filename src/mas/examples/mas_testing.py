"""Test file for basic MAS"""

from app import App

from mas.ag2.ag2_agent import AG2MASAgent
from mas.ag2.ag2_task import AG2Task
from mas.base_resource import BaseResource
from mas.multi_agent_system import MultiAgentSystem
from mas.query.mas_query import MASQuery
from mas.resources.empty import EmptyResource
from mas.resources.text import TextResource
from mas.task import Task
from mas.tasks.write_sentence import SentenceResource, TopicResource
from utils.string_template import generate_str_using_template


def test_basic_mas(app: App):
    """Test basic MAS."""

    mas = MultiAgentSystem()

    yaml_file = "./resource/example/example3.yaml"

    mas_query = MASQuery.from_yaml(yaml_file)

    print(
        mas_query.model_dump_json(indent=4, exclude_unset=True, exclude_defaults=True)
    )

    # TODO create a class that can contains this mapping and allows you add to it
    # TODO includes aliases for mapping also
    # example resources mapping
    example_resource_mapping: dict[str, type[BaseResource]] = {
        "sentence": SentenceResource,
        "topic": TopicResource,
    }

    mas.add_resource_types_from_dict(example_resource_mapping)

    agent = AG2MASAgent(
        name="AssistantAgent",
        description="You are an assistant.",
        llm_config=app.config_manager.get_llm_config(use_tools=False),
    )

    # example tasks
    example_tasks: list[Task] = [
        # write a sentence about a topic
        AG2Task(
            name="WriteSentenceTask",
            description="Write a sentence about a topic.",
            input_resource=TopicResource,
            output_resource=SentenceResource,
            generate_str=generate_str_using_template(
                "Write a sentence about {topic}",
            ),
            agent=agent,
        ),
        # capitalise a sentence
        AG2Task(
            name="CapitaliseSentenceTask",
            description="Capitalise a sentence.",
            input_resource=SentenceResource,
            output_resource=TextResource,
            generate_str=generate_str_using_template(
                "Capitalise the sentence: {sentence}",
            ),
            agent=agent,
        ),
        # think of a topic
        AG2Task(
            name="ThinkOfTopicTask",
            description="Think of a topic.",
            input_resource=EmptyResource,
            output_resource=TopicResource,
            generate_str=generate_str_using_template(
                "Think of a topic to write about.",
            ),
            agent=agent,
        ),
    ]

    # add tasks to mas
    for task in example_tasks:
        mas.add_task(task)

    mas.solve_query(mas_query)
