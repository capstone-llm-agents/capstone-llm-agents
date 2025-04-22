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

        about: str
        """The topic to be represented by the resource."""

        def __init__(self, about: str):
            """
            Initialise the TopicModel with a topic.

            Args:
                about (str): The topic to be represented by the resource.
            """
            super().__init__(topic=about)
            self.about = about

    def __init__(self, about: TopicModel):
        """
        Initialise the TopicResource with a topic.

        Args:
            about (str): The topic to be represented by the resource.
        """
        super().__init__(about)
        self.topic = about


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
        topic = input_resource.topic.about
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
