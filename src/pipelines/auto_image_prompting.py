from functools import partial
import re

########################################################
#                                                      #
#          Find Entities In The Sentences              #
#                                                      #
########################################################

ENTITIES = """\
Here is a text in which you have to detect each entity which could be described physically. \
All detected entity have to be things that could be impressed in a photo. They can't be abstract things.
  
Text: {sentences}
Entities (divided by commas):"""

def entities_detection(model, sentences, prompt = ENTITIES):
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

# GET_IMAGE_DESCRIPTION = """It's a bot to traduce sentences of a children's story in image

# Context: It's part of an app to generate illustrated text.\
# So the bot receives some sentences of a text and the previos images description.\
# It also receives a process to think step by step for generating the description of the image which illustrates the situation is described in those sentences.\
# In addition it receives a very detail physical description for each entity in the sentences.\
# It should use those physical description to describe the final image.\ 
# In addition the bot receives some rules which they can't be broken for generating the description image.\
# Finally it given us a very detail description of some photo of this situation.\

# Process for generating the description step by step:
# 1 - Read the sentences and find the four main elements needed to construct an image.\
# The main action of the text, who performs it, who or what is the goal of this action and where it takes place.
# 2 - Detect each entity who has been described into the sentences. 
# 3 - Read the description of the previous image to compare the contexts of the situations,\
# to understand how the transition from one image to the other occurs and to keep the description of the characters,\
# if both sentences speak of the same people.
# 4 - Decide whether the sentences speak of a continuation of the previous image or describe a different context.\
# If the context is different, imagine the context.
# 5 - Imagine a photo in which you can see how the protagonist of the detected action performs that action within\
# the detected context and being consistent with the selected context of the step 3.
# 6 - Being coherent with the selected context of the step 3, the physical entity descriptions and following the rules of generation that are marked.\
# Generating a very detailed description of an image, based on the described structure,\
# that can capture the full meaning of the situation described in the sentences. 

# Rules:
# - It have to be careful with the information in the sentence.\
# In the final description, there don't have to be things which aren't in the sentences
# - It have to be careful with how many people there are in the sentences.\
# If the sentences talk only about one person, in the description can't be more than one
# - It have to pay attention when the sentence talk only about a part of something.\
# In that case the description should make emphasis in this part even it could omit the subject  
# - It have to describe people with their backs turned whenever the context of the sentences allows it
# - It must be very rigorous with the descriptions of the entities. They must match exactly with the descriptions provided.

# Physical Entities Description:
# {entities}

# Previous Image Description:
# {description}

# Sentences:
# {sentences}

# Image Description:
# """

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
    return 'Photo in long plane of ' + model.text2text(prompt.format(sentences = sentences, log_text  = log_text))


########################################################
#                                                      #
#          Formatter                                   #
#                                                      #
########################################################


FORMATTER = """It's a complement of the bot to traduce sentences of a children's story in image

Context: There is a bot that receives some sentences of a children's story and return\
the description of an image which show the frame of the story which is described in the sentences.\
But the images' prompt need to have an specific structure,\
so this complement is a function to transform the description to image prompt with a better structure.\
This bot receives the sentences and the image description then return an image prompt with a better structure.\
The structure of image prompt is defined like a text which start with a sentences of main image information,\
action or topic where each noun are between parenthesis and after that there is a very detail image description   

Sentences:
Once upon a time there was a young girl named Lily who loved to explore the forest near her home.

Description:
Lily exploring the forest. Lily is standing in a clearing in the forest,\
wearing a red dress and a matching red hat, her hands clasped in front of her in excitement.\
She has a look of wonder on her face as she takes in the beauty of the trees around her.\
The sun is shining down, casting a warm light through the leaves.\
In the background, a large tree can be seen, its trunk stretching up to the sky.

Image Prompt:
((Lily)) in the ((forest)) near to a ((home)).\
Lily is standing in a clearing in the forest, wearing a red dress and a matching red hat,\
her hands clasped in front of her in excitement.\
She has a look of wonder on her face as she takes in the beauty of the trees around her.\
The sun is shining down, casting a warm light through the leaves.\
In the background, a large tree can be seen, its trunk stretching up to the sky.

Sentences:
Every day, the child would take a basket and go deep into the forest to find new plants and animals.

Description:
The child stands in the middle of the forest, with a basket in one hand,\
looking around with curiosity and a sense of adventure. The sun is setting in the background,\
painting the sky in a beautiful pink and orange hue. The child wears a light blue dress,\
a backpack on their back, and looks around, ready to explore the depths of the forest and find new plants and animals.

Image Prompt:
A ((child)) with ((basket)) is watching ((plants)) and ((animals)) in the ((forest)).\
The child stands in the middle of the forest, with a basket in one hand,\
looking around with curiosity and a sense of adventure. The sun is setting in the background,\
painting the sky in a beautiful pink and orange hue. The child wears a light blue dress,\
a backpack on their back, and looks around, ready to explore the depths of the forest and find new plants and animals.

Sentences:
{sentences}

Description:
{description}

Image Prompt:
"""

def image_description_formatter(model, sentences, description, prompt = GET_IMAGE_DESCRIPTION):
    return model.text2text(prompt.format(
        sentences = sentences, description  = description
    ))



########################################################
#                                                      #
#          Pipeline                                    #
#                                                      #
########################################################


class TestIllustrateModel:    
    def __init__(
        self, 
        model, 
        p_entities = ENTITIES, 
        p_entity_description = GET_ENTITY_DESCRIPTIONS,
        p_image_description = GET_IMAGE_DESCRIPTION,
        p_image_formatter = FORMATTER
    ) -> None:
        self.model = model
        self.p_entities = p_entities
        self.p_entity_description = p_entity_description
        self.p_image_description = p_image_description
        self.p_image_formatter = p_image_formatter
        
        self.logger = '............. {action}'

    def run(self, text, frames, style=''):
        print(self.logger.format(action = 'init inferences 🏭'))
        
        self.entities = {}
        entity_list = entities_detection(self.model, text, self.p_entities)
        print(self.logger.format(action = 'the entities was detected 🕵🏽‍♂️'))

        for entity in entity_list:
            self.entities[entity] = generate_entity_description(self.model, text, entity, self.p_entity_description)
            print(self.logger.format(action = f'the entity {entity} was described ✍🏽'))

        for i, f in enumerate(frames):
            print(self.logger.format(action = f'analyzing {i}/{len(frames)} frame 🧐'))
            image_prompt, _ = self.pipeline(f, text, self.entities, style)
            yield image_prompt

    def pipeline(self, frame, text, entities: dict = None, style = ''):
        if not entities:
            entities = {}

        entity_list = entities_detection(self.model, frame, self.p_entities)

        for entity in entity_list:
            if entity not in entities:
                entities[entity] = generate_entity_description(self.model, text, entity, self.p_entity_description)
                print(self.logger.format(action = f'the entity {entity} was described ✍🏽'))

        image_description = generate_image_description(self.model, frame, text, self.p_image_description)
        print(self.logger.format(action = f'the image description was generated 🤩'))

        selected_entities = []
        for entity in entities.keys():
            top, temp = 0, ''
            for match in re.finditer(entity.lower(), image_description, re.IGNORECASE):
                i, j = match.span()
                selected_entities.append((i, entity))
                temp += image_description[top:i] + f'(({entity}))'
                top = j
            
            
            if top:
                image_description = temp + image_description[top:]

        if style:
            image_description += f' ((({style}))).'
        
        sett = set()
        for _, entity in filter(lambda x: x[1] not in sett, sorted(selected_entities)):
            image_description += '\n' + entities[entity]
            sett.add(entity)    

        # formatted_image_description = image_description_formatter(self.model, frame, image_description, self.p_image_formatter)
        print(self.logger.format(action = f'the image description was formatted 🙌🏽'))

        return image_description, entities
