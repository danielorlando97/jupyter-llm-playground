from functools import partial
import re
from dataclasses import dataclass
########################################################
#                                                      #
#          Find Entities In The Sentences              #
#                                                      #
########################################################

ENTITIES = """\
Here is a text in which you have to detect each entity which could be described physically. \
All detected entity have to be things that could be impressed in a photo. They can't be abstract things. \
  
Text: {sentences}
Entities (divided by commas):"""

def entities_detection(model, sentences, prompt = ENTITIES):
    entities : str = model.text2text(prompt.format(sentences = sentences))
    
    if entities.endswith('.'):
        entities = entities[:-1]

    return list(map(lambda x: x.strip().lower(),  entities.split(',')))


ENTITIES = """\
Here is a text in which you have to detect its main characters.
  
Text: {sentences}
Characters (divided by commas):"""

def characters_detection(model, sentences, prompt = ENTITIES):
    entities : str = model.text2text(prompt.format(sentences = sentences))
    
    if entities.endswith('.'):
        entities = entities[:-1]

    return list(map(lambda x: x.strip().lower(),  entities.split(',')))

########################################################
#                                                      #
#          Get Entity Description                      #
#                                                      #
########################################################

# GET_ENTITY_DESCRIPTIONS = """I gave you a story and a story's entity .\
# Give me a very detail physical description for this entity. \
# Talk me about its physic and its clothes. \
# Don't talk me about its personality.

# Story: {story}

# Entity: {entity}

# Descriptions:
# {entity_name} """


# GET_ENTITY_DESCRIPTIONS = """I gave you a story and a story's entity .\
# Give me a very detail physical description for this entity. \
# Talk me about its physic and its clothes. \
# Don't talk me about its personality.

# Story: {story}

# Entity: {entity}

# Descriptions:
# {entity_name} """

GET_ENTITY_DESCRIPTIONS = """\
Here is a log text and a question about one of the things in this text. \
This question is about the physical description of this thing. \
To answer this question, first, you should imagine a photo of this thing and \
after that make a very detail physical description of this thing. \
You only hace to talk about its physic and maybe about its clothes. \
But you mustn't talk about its personality or its mood. \

Text: {text}
Question: You have a photo of {entity} in front of you. What does {entity} look like in this photo?
Answer: {entity_name} """

def generate_entity_description(model, text, entity, prompt = GET_ENTITY_DESCRIPTIONS):
    name = entity[0].upper() + entity[1:]
    return f'{name} ' + model.text2text(prompt.format(text = text, entity  = entity, entity_name = name))

########################################################
#                                                      #
#          Get Image Description                       #
#                                                      #
########################################################

GET_IMAGE_DESCRIPTION = """Describe a image to represent the described situation in some sentences of a log text. \
Give a very detail description of the image, explain me the position of each element into the image. \
Don't talk me about styles, psychical descriptions, personality descriptions, clothing or face expressions. \
Give me only the distribution of each element in the image and their position between one with other. \

Log Text:
{log_text}

Sentences:
{sentences}

Image Description:
Photo in long plane of """


def generate_image_description(model, sentences, log_text, prompt = GET_IMAGE_DESCRIPTION):
    return model.text2text(prompt.format(sentences = sentences, log_text  = log_text))


SUMMARY_DESCRIPTION = """Here is a very detail image description. But I only need one sentence witch describes the image. \
So, give a sentences witch summaries the very detail image description.

Very Detail Image Description: {description}
Summary: """

def summary_description(model, description):
    summ = model.text2text(SUMMARY_DESCRIPTION.format(description = description))
    if summ.endswith('.'):
        return summ[:-1]
    return summ


SEMANTIC_IMAGE_DESCRIPTION = """\
There is a book for children where there are some very nice stories. \
Each story is divided into some pages of the book and \
each page has some sentences of some story and \
a picture to illustrate what happens in those sentences. \
Below is one of the stories in the book, \
physical descriptions of some things in this story and \
the text on one of the pages of this story. 

Story: 
{story}

Descriptions:
{descriptions}

Text on the pages:
{text}

Question: Write a very detailed description of the picture that should be on the same page as that text. \
{question_details}

Answer: A photo of""" 


SEMANTIC_IMAGE_DESCRIPTION_EXTENSION = """\
Describe the position of each element in the picture and they relation between them. \
Also describe how is each element in the picture. \
But don't talk about the artistic styles. \
Only describe the composition of the picture and each its elements."""

def build_semantic_description(model, story: str, descriptions: list, text: str, explain =False):
    description = ''
    for values in descriptions:
        description += f' - {values}\n'

    prompt = SEMANTIC_IMAGE_DESCRIPTION.format(
        story=story, 
        descriptions=description, 
        text = text,
        question_details = '' if not explain else SEMANTIC_IMAGE_DESCRIPTION_EXTENSION
    )
    g_prompt = model.text2text(prompt)

    return g_prompt


########################################################
#                                                      #
#          Formatter                                   #
#                                                      #
########################################################

Formatter = """Drop each pronoun from the following text and enter the noun that is being replaced by the pronoun.

Text: {text}

Transformed Text:"""

def formatter(model, text):
    new_text = model.text2text(Formatter.format(text))

    return new_text.split('.')

########################################################
#                                                      #
#          Pipeline                                    #
#                                                      #
########################################################


class IllustrateModel:
    def __init__(self, model, descriptions_len = 1) -> None:
        self.model = model
        self.descriptions_len = descriptions_len
        self.logger = '............. {action}'

        self.entity_detection = characters_detection
        self.entity_description = generate_entity_description

    def run(self, text, frames, style='any', frame = 'photo'):
        print(self.logger.format(action = 'init inferences 🏭'))
        
        self.entities = {}
        self.entity_list = self.entity_detection(self.model, text)
        print(self.logger.format(action = 'the entities was detected 🕵🏽‍♂️'))

        for entity in self.entity_list:
            self.entities[entity] = self.entity_description(self.model, text, entity)
            print(self.logger.format(action = f'the entity {entity} was described ✍🏽'))

        for i, f in enumerate(frames):
            print(self.logger.format(action = f'analyzing {i}/{len(frames)} frame 🧐'))
            subject, descriptions = self.pipeline(f, text, self.entities)
            yield self.image_prompt_structure(
                subject=subject,
                frame=frame,
                styles=style,
                descriptions=descriptions[:self.descriptions_len + 1]
            )

    def pipeline(self, frame, text, entities: dict = None):
        return 'a cat', []

    def image_prompt_structure(self, subject = '', styles='', frame = '', descriptions=''):
        return f"A {frame} in the {styles} style of {subject}"
    

class MultiDescriptionModel(IllustrateModel):    

    def pipeline(self, frame, text, entities: dict = None):
        descriptions, subject = [], ''

        if not entities:
            entities = {}

        image_pos_description = generate_image_description(self.model, frame, text)
        print(self.logger.format(action = f'the image description was generated 🤩'))
        descriptions.append(image_pos_description)

        if self.attention_summary:
            subject = summary_description(self.model, image_pos_description)

        selected_entities = []
        for entity in entities.keys():
            if (re.search(entity.lower(), image_pos_description, re.IGNORECASE)):
                selected_entities.append(entity)
        
        for entity in self.entity_list:

            if entity in selected_entities:
                descriptions.append(entities[entity])

        print(self.logger.format(action = f'the image description was formatted 🙌🏽'))

        return subject, descriptions

    def image_prompt_structure(self, subject = '', styles='', frame = '', descriptions=''):
        return f"A {frame} in the {styles} style where {'In Addition, '.join(descriptions)}"



class WellDescribedModel(IllustrateModel):

    def __init__(self, model, descriptions_len=1, explain = False) -> None:
        super().__init__(model, descriptions_len)

        self.entity_detection = entities_detection
        self.explain = explain

    def pipeline(self, frame, text, entities: dict = None):
        subject = build_semantic_description(self.model, text, entities.values(), frame, explain= self.explain)
        print(self.logger.format(action = f'the image description was generated 🤩'))

        return subject, []

    def image_prompt_structure(self, subject = '', styles='', frame = '', descriptions=''):
        return f"A {frame} in the {styles} style of {subject}"