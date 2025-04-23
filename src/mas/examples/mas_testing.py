"""Test file for basic MAS"""

from app import App

from mas.ag2.ag2_agent import AG2MASAgent
from mas.ag2.ag2_task import AG2Task
from mas.base_resource import BaseResource
from mas.multi_agent_system import MultiAgentSystem
from mas.query.mas_query import MASQuery
from mas.resources.empty import EmptyResource
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
        "empty": EmptyResource,
        "sentence": SentenceResource,
        "topic": TopicResource,
    }

    mas.add_resource_types_from_dict(example_resource_mapping)

    agent = AG2MASAgent(
        name="AssistantAgent",
        description="You are an assistant.",
        llm_config=app.config_manager.get_llm_config(use_tools=False),
    )

    write_sentence_task = AG2Task(
        name="WriteSentenceTask",
        description="Write a sentence about a topic.",
        input_resource=TopicResource,
        output_resource=SentenceResource,
        generate_str=generate_str_using_template(
            "Write a sentence about '{topic}'",
        ),
        agent=agent,
    )

    # using LLM
    capatilise_sentence_task = AG2Task(
        name="CapitaliseSentenceTask",
        description="Makes the sentence all capitals.",
        input_resource=SentenceResource,
        output_resource=SentenceResource,
        generate_str=generate_str_using_template(
            "Make the sentence in all capitals: '{sentence}'. Make sure the JSON response is formatted correctly.",
        ),
        agent=agent,
    )

    think_of_topic_task = AG2Task(
        name="ThinkOfTopicTask",
        description="Think of a topic.",
        input_resource=EmptyResource,
        output_resource=TopicResource,
        generate_str=generate_str_using_template(
            "Think of a topic to write about. Kept it less than 5 words.",
        ),
        agent=agent,
    )

    descriptor_mapping: dict[str, Task] = {
        "about_topic": write_sentence_task,
        "is_capitalised": capatilise_sentence_task,
    }

    # example tasks
    example_tasks: list[Task] = [
        # write a sentence about a topic
        write_sentence_task,
        # capitalise a sentence
        capatilise_sentence_task,
        # think of a topic
        think_of_topic_task,
    ]

    # add tasks to mas
    for task in example_tasks:
        mas.add_task(task)

    output_resources = mas.solve_query(mas_query, descriptor_mapping)

    # print the output resources
    print("Output:")
    for output_resource in output_resources:
        print(output_resource.model.model_dump_json(indent=4, exclude_unset=True))
