"""Module for testing the task system"""

# TODO remove later just for example testing


from app import App
from mas.ag2.ag2_agent import AG2MASAgent
from mas.ag2.ag2_task import AG2Task
from mas.resources.param_template import ParamTemplateResource
from mas.resources.params import ParamsResource
from mas.resources.text import TextResource
from mas.tasks.param_string_task import ParamStringTask
from mas.tasks.write_sentence import TopicResource, WriteSentenceTask
from utils.string_template import generate_str_using_template


def test_task(app: App):
    """Test the task system"""

    # write sentence example
    task = WriteSentenceTask()

    sentence = task.do(TopicResource(TopicResource.TopicModel("cats")))

    print(sentence.sentence.sentence)

    # param string example

    param_task = ParamStringTask()
    param_template = param_task.do(
        ParamTemplateResource(
            ParamTemplateResource.ParamTemplateModel(
                template_str=TextResource.TextModel(text="The {topic} is a great pet."),
                params=ParamsResource.ParamsModel(params={"topic": "cat"}),
            )
        )
    )

    print(param_template.text.text)

    agent = AG2MASAgent(
        name="AG2MAS",
        description="Write a sentence about a topic.",
        llm_config=app.config_manager.get_llm_config(use_tools=False),
    )

    # ag2 task
    ag2_task = AG2Task(
        name="AG2Task",
        description="Write a sentence about a topic.",
        input_resource=TopicResource,
        output_resource=TextResource,
        generate_str=generate_str_using_template(
            "Write a sentence about {topic}",
        ),
        agent=agent,
    )

    res = ag2_task.do(
        TopicResource(TopicResource.TopicModel("cats")),
    )

    print(res.text.text)
