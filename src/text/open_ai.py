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

@dataclass
class ChatMessage:
    role : Union [Literal["user"], Literal["assistant"], Literal['system']]
    content: str

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, index):
        return self.__dict__[index]

class OpenAIChatGeneration:
    def __init__(self, model: Model = 'gpt-3.5-turbo') -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.engine = model

    def body_compose(self, config: OpenAITextModelConfig, **info):
        body = {
            ** config,
            ** info,
            'model' : self.engine
        }

        return body

    def text2text(self, prompt: str, config: OpenAITextModelConfig = OpenAITextModelConfig(), previous_talk = []) -> tuple[ChatMessage, ChatMessage]:
        messages = ChatMessage(role='user', content=prompt)
        body = self.body_compose(config, messages = [{**m} for m in previous_talk + [messages]])
        response = openai.ChatCompletion.create(**body)
        return ChatMessage('assistant', response.choices[0].message.content.strip()), messages
    


PRESENTATION = """You are a bot with Jim Lee's creativity. \
You were designed to imagine the physical description of things of the following text or \
to describe an image which illustrate some part of the following text.

Text: {story}

Users can ask you two kind of question, but he can repeat the same questions many times and \
you have always to give him new information about the topic. If you have already said something about \
something or somebody don't repeat the same information.   

1- What does something or somebody look like. \
In that case, first, you have to image how it look like. \
After that answer with a very short and concrete sentence about the physical description of it. \
Don't talk about its personality, its mood or its expression. \
For talking about its clothes write a new very short and concrete sentence about its clothes and \
begins with the target's name.

2- How look the image which illustrate some literal part of the text like. \
In that other case you hace to answer with a very detail description of the illustration which \
are in the same page of the book that some literal part of the text are. You have to describe \
the composition of the image and the position of each its element. But you don't have to talk \
about image styles or physical description of its elements.
"""

SET_TEXT = """Text: {story}"""

class TextIllustratorAssistant(OpenAIChatGeneration):
    def __init__(self, model='gpt-3.5-turbo', config: OpenAITextModelConfig = OpenAITextModelConfig()) -> None:
        super().__init__(model)

        self.config = config

    def fit(self, stroy):
        self.conversation = [ChatMessage('system', PRESENTATION.format(story = stroy))]

    
    def entity_describe(self, entity):
        self.conversation.append(ChatMessage('system', content=f'Think that you have a photo of {entity} in front of you'))

        answer, question = self.text2text(
            f'What does {entity} look like?', 
            self.config, 
            self.conversation
        )

        self.conversation.append(question)
        self.conversation.append(answer)

        return answer.content
    
    def image_describe(self, frame):
        answer, question = self.text2text(
            f'How look the image which illustrate the following literal part of the text like? \
                Literal part of the text: {frame}', 
            self.config, 
            self.conversation
        )

        self.conversation.append(question)
        self.conversation.append(answer)

        return answer.content