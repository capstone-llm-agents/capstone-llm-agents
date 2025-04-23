"""Module to run a simple model using Autogen2 to complete a basic task of writing a sentence about a topic."""

from pydantic import BaseModel

# topic resource
from mas.base_resource import BaseResource
from mas.task import Task


class TopicResource(BaseResource):
    """A resource representing a topic."""

    # topic model
    class TopicModel(BaseModel):
        """A model representing a topic."""

        topic: str
        """The topic to be represented by the resource."""

        def __init__(self, topic: str):
            """
            Initialise the TopicModel with a topic.

            Args:
                topic (str): The topic to be represented by the resource.
            """
            super().__init__(topic=topic)
            self.topic = topic

    def __init__(self, topic: TopicModel):
        """
        Initialise the TopicResource with a topic.

        Args:
            topic (str): The topic to be represented by the resource.
        """
        super().__init__(topic)
        self.topic = topic

    @staticmethod
    def get_model_type() -> type[TopicModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        return TopicResource.TopicModel


class SentenceResource(BaseResource):
    """A resource representing a sentence."""

    # sentence model
    class SentenceModel(BaseModel):
        """A model representing a sentence."""

        sentence: str
        """The sentence to be represented by the resource."""

        def __init__(self, sentence: str):
            """
            Initialise the SentenceModel with a sentence.

            Args:
                sentence (str): The sentence to be represented by the resource.
            """
            super().__init__(sentence=sentence)
            self.sentence = sentence

    def __init__(self, sentence: SentenceModel):
        """
        Initialise the SentenceResource with a sentence.

        Args:
            sentence (str): The sentence to be represented by the resource.
        """
        super().__init__(sentence)
        self.sentence = sentence

    @staticmethod
    def get_model_type() -> type[SentenceModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        return SentenceResource.SentenceModel


class WriteSentenceTask(Task[TopicResource, SentenceResource]):
    """A task that writes a sentence about a topic."""

    def _do_work(self, input_resource: TopicResource) -> SentenceResource:
        """
        Perform the task using the input resource.

        Args:
            input_resource (TopicResource): The input resource for the task.

        Returns:
            SentenceResource: The output resource after performing the task.
        """
        topic = input_resource.topic.topic
        sentence = f"This is a sentence about {topic}."
        return SentenceResource(SentenceResource.SentenceModel(sentence=sentence))

    def __init__(self):
        """
        Initialise the WriteSentenceTask.
        """
        super().__init__(
            "WriteSentenceTask",
            "A task that writes a sentence about a topic.",
            TopicResource.TopicModel,
            SentenceResource.SentenceModel,
            self._do_work,
        )
