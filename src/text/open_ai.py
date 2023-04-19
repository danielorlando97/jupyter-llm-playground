import openai
from typing import Union, Literal
import os
from dataclasses import dataclass

Model = Union[
    Literal['text-davinci-002'],
    Literal['text-davinci-003'],
]

@dataclass
class OpenAITextModelConfig:
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: int = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, index):
        return self.__dict__[index]


class OpenAITextGeneration:
    def __init__(self, model: Model = 'text-davinci-003') -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.engine = model

    def body_compose(self, config: OpenAITextModelConfig, **info):
        body = {
            ** config,
            ** info,
            'engine' : self.engine
        }

        return body

    def text2text(self, prompt: str, config: OpenAITextModelConfig = OpenAITextModelConfig()) -> str:
        body = self.body_compose(config, prompt = prompt)
        response = openai.Completion.create(**body)
        return response.choices[0].text.strip()