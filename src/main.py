"""Entry point of the program."""

from app import App
from examples.write_sentence import TopicResource, WriteSentenceTask
from mas.ag2.ag2_agent import AG2MASAgent
from mas.ag2.ag2_task import AG2Task
from mas.resources.param_template import ParamTemplateResource
from mas.resources.params import ParamsResource
from mas.resources.text import TextResource
from mas.tasks.param_string_task import ParamStringTask


def main():
    """Entry point of the program."""
    app = App()
    app.run()

    # write sentence example
    task = WriteSentenceTask()

    sentence = task.do_work(TopicResource(TopicResource.TopicModel("cats")))

    print(sentence.sentence.sentence)

    # param string example
    param_task = ParamStringTask()
    param_template = param_task.do_work(
        ParamTemplateResource(
            ParamTemplateResource.ParamTemplateModel(
                template_str=TextResource.TextModel(text="The {topic} is a great pet."),
                params=ParamsResource.ParamsModel(
                    params={"topic": sentence.sentence.sentence}
                ),
            )
        )
    )

    print(param_template.text.text)

    agent = AG2MASAgent(
        name="AG2MAS",
        description="Write a sentence about a topic.",
        llm_config=app.config_manager.get_llm_config(use_tools=False),
        response_format=TextResource.TextModel,
    )

    # ag2 task
    ag2_task = AG2Task(
        input_resource=TopicResource,
        output_resource=TextResource,
        str_template="Write a sentence about {topic}.",
        agent=agent,
    )

    res = ag2_task.do_work(
        TopicResource(TopicResource.TopicModel("cats")),
    )

    print(res.text.text)


if __name__ == "__main__":
    main()
