import os
from typing import Any, List

from openai import OpenAI

from mbodied.base.backend import Backend
from mbodied.base.serializer import Serializer
from mbodied.types.message import Message
from mbodied.types.vision import Image


class OpenAISerializer(Serializer):
    """Serializer for OpenAI-specific data formats."""

    @classmethod
    def serialize_image(cls, image: Image) -> dict[str, Any]:
        """Serializes an image to the OpenAI format.

        Args:
            image: The image to be serialized.

        Returns:
            A dictionary representing the serialized image.
        """
        return {
            "type": "image_url",
            "image_url": {
                "url": image.url,
            },
        }

    @classmethod
    def serialize_text(cls, text: str) -> dict[str, Any]:
        """Serializes a text string to the OpenAI format.

        Args:
            text: The text to be serialized.

        Returns:
            A dictionary representing the serialized text.
        """
        return {"type": "text", "text": text}


class OpenAIBackend(Backend):
    """Backend for interacting with OpenAI's API."""

    INITIAL_CONTEXT = [
        Message(role="system",
                content='You are a robot with advanced spatial reasoning.'),
    ]
    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, api_key: str | None, client: OpenAI | None = None, response_format: str = None, **kwargs):
        """Initializes the OpenAIBackend with the given API key and client.

        Args:
            api_key: The API key for the OpenAI service.
            client: An optional client for the OpenAI service.
            response_format: The format for the response.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"), client=client)
        if self.client is None:
            self.client = OpenAI(api_key=self.api_key)
        self.serialized = OpenAISerializer
        self.response_format = response_format

    def _create_completion(self, messages: List[Message], model: str = "gpt-4o", stream: bool = False, **kwargs) -> str:
        """Creates a completion for the given messages using the OpenAI API.

        Args:
            messages: A list of messages to be sent to the completion API.
            model: The model to be used for the completion.
            stream: Whether to stream the response. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The content of the completion response.
        """
        serialized_messages = [self.serialized(msg) for msg in messages]

        completion = self.client.chat.completions.create(
            model=model,
            messages=serialized_messages,
            temperature=0,
            max_tokens=1000,
            stream=stream,
            response_format=self.response_format,
            **kwargs,
        )
        return completion.choices[0].message.content