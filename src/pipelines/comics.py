import re
from functools import partial
########################################################
#                                                      #
#          Generate Mainly Story                       #
#                                                      #
########################################################

COMICS_GENERATE = """This is a bot to write long stories for children.\
    
Context:\
The bot's stories usually have a very important lesson for children.\
Today the bot will talk them about {prompt}.\
When this bot talks about people it doesn't use world like child, person, human.\
It always uses world which expresses the person's generous, like boy, man, woman, girl.\
It also invent a very funny name for each character and place.\

Story:
Once upon a time"""

def generate_comic(model, prompt):
    comics = model.text2text(COMICS_GENERATE.format(prompt=prompt))
    return "Once upon a time " + comics

########################################################
#                                                      #
#          Split Mainly Story In Frames                #
#                                                      #
########################################################


SPLIT_STORY = """This is a bot to split stories in principal frames.
    
Story:
Manuel was a very curious little boy.\
One day, he saw a sign that said "Beware of the forest" and he wanted to see what was inside.\
So he went in.

Answer:
1-Manuel was a very curious little boy. One day, he saw a sign that said "Beware of the forest"
2-He wanted to see what was inside. So he went in.

Story:
Manuel saw all kinds of animals in the forest.\
He saw a deer, a rabbit, and even a bear!\
He was so excited to see all of these animals.\
But then, Manuel saw a big, scary snake.\
The snake was coiled up and ready to strike.\
Manuel was so scared that he ran out of the forest as fast as he could.

Answer:
1-Manuel saw all kinds of animals in the forest.
2-He saw a deer.
3-He saw a rabbit.
4-He even saw a bear!
5-He was so excited to see all of these animals.
6-But then, ....
7-Manuel saw a big, scary snake. The snake was coiled up and ready to strike.
8-Manuel was so scared that he ran out of the forest as fast as he could.

Story:
When he got home, he was so happy to be safe.\
He learned that it is always important to listen to warnings and to be careful when exploring new places.

Answer:
1-When he got home, he was so happy to be safe.
2-He learned that it is always important to listen to warnings and to be careful when exploring new places.

Story:
Manuel was a very curious little boy.\
One day, he saw a sign that said "Beware of the forest" and he wanted to see what was inside.\
So he went in.\
Manuel saw all kinds of animals in the forest.\
He saw a deer, a rabbit, and even a bear!\
He was so excited to see all of these animals.\
But then, Manuel saw a big, scary snake.\
The snake was coiled up and ready to strike.\
Manuel was so scared that he ran out of the forest as fast as he could.\
When he got home, he was so happy to be safe.\
He learned that it is always important to listen to warnings and to be careful when exploring new places.
 
Answer:
1-Manuel was a very curious little boy. One day, he saw a sign that said "Beware of the forest"
2-He wanted to see what was inside. So he went in.
3-Manuel saw all kinds of animals in the forest.
4-He saw a deer.
5-He saw a rabbit.
6-He even saw a bear!
7-He was so excited to see all of these animals.
8-But then, ....
9-Manuel saw a big, scary snake. The snake was coiled up and ready to strike.
10-Manuel was so scared that he ran out of the forest as fast as he could.
11-When he got home, he was so happy to be safe.
12-He learned that it is always important to listen to warnings and to be careful when exploring new places.

Story:
{story}

Answer:
1-"""

def text_splitter(model, story):
    splits = '1-' + model.text2text(SPLIT_STORY.format(story = story))
    frames = re.split(r'\d+-\s*', splits.strip())
    return frames[1:]



########################################################
#                                                      #
#          Pipeline                                    #
#                                                      #
########################################################


def pipeline(model, prompt):
    story = generate_comic(model, prompt)
    frames = text_splitter(model, story)

    return story, frames