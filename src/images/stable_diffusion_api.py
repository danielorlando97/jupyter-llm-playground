# Reference  https://stablediffusionapi.com/

import json
import os
from dotenv import load_dotenv
import requests
from dataclasses import dataclass
from typing import Union, Literal
import time

load_dotenv()

Model = Union[
    None,
    Literal['midjourney'],
]


@dataclass
class StableDiffusionApiModelConfig:
    strength: float = 0.7
    num_inference_steps: int = 30
    seed: int = 0
    guidance_scale: float = 7.5

    width: int = 512
    height: int = 512
    samples: int = 1
    safety_checker: str = "yes"
    track_id: str = None

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, index):
        return self.__dict__[index]


INIT_LABEL = """
#########################################################################
    Init Stable Diffusion System (ApiKey = {key}) 
#########################################################################
"""

SAVED_SEED_LABEL = '......... saving seed {seed}'
GENERATE_SEED_LABEL = '......... generate by seed {seed}'
GENERATING_LABEL = "......... wait I'm generating 🙃"
ERROR_LABEL = "......... There has been an error 😭. The model say '{message}'"


def formatter(f):
    def ff(self, *arg, **kwd):
        result = f(self, *arg, **kwd)

        if result and hasattr(self, 'output_formatter'):
            return self.output_formatter(result)

        return result

    return ff


class StableDiffusionApi:
    def __init__(self, model: Model = None, save_seed=False, image_formatter=lambda p: p, prompt_suffix = None) -> None:
        self.key = os.getenv("SDAPI_API_KEY")
        self.model_id = model
        self.save_seed = save_seed
        self.output_formatter = image_formatter
        self.prompt_suffix = prompt_suffix

        if model:
            self.base_url = 'https://stablediffusionapi.com/api/v3/dreambooth/'
        else:
            self.base_url = 'https://stablediffusionapi.com/api/v3/'

        # print(INIT_LABEL.format(key=self.key))

    def body_compose(self, config: StableDiffusionApiModelConfig, prompt, **info):
        body = {
            ** config,
            ** info,
            "prompt": prompt if not self.prompt_suffix else f'{self.prompt_suffix} {prompt}',
            "webhook": None,
            'key': self.key
        }

        if self.model_id:
            body['model_id'] = self.model_id

        if hasattr(self, 'seed'):
            body['seed'] = self.seed

        return body

    def request(self, tag, body):

        r = requests.post(
            self.base_url + tag,
            data=json.dumps(body),
            headers={'Content-Type': 'application/json'})

        res = r.json()

        if res['status'] == 'failed':
            print(ERROR_LABEL.format(message=res['messege']))
            return

        if self.save_seed and not hasattr(self, 'seed'):
            self.seed = res['meta']['seed']
            print(SAVED_SEED_LABEL.format(seed=self.seed))
        else:
            print(GENERATE_SEED_LABEL.format(seed=res['meta']['seed']))

        result = res
        while result['status'] == 'processing':
            print(GENERATING_LABEL)
            time.sleep(5)
            result = requests.post(
                res['fetch_result'],
                data=json.dumps({'key': self.key}),
                headers={'Content-Type': 'application/json'}
            )

            result = result.json()

        return result['output']

    @formatter
    def text2image(self, prompt, neg='', config: StableDiffusionApiModelConfig = StableDiffusionApiModelConfig()):
        """
        :param str prompt: Your Prompt 
        :param str neg: Items you don't want in the image 
        :param StableDiffusionApiModelConfig config: Your hyperparams for the generation
        """
        body = self.body_compose(config, prompt, negative_prompt=neg)
        images = self.request('text2img' if not self.model_id else '', body)

        return images

    @formatter
    def in_painting(self, prompt: str,  image: str, mask: str, neg='', config: StableDiffusionApiModelConfig = StableDiffusionApiModelConfig()):
        """
        :param str prompt: Your Prompt 
        :param str neg: Items you don't want in the image 
        :param str image: link of Initial Image 
        :param str mask: link of mask image for inpainting
        :param StableDiffusionApiModelConfig config: Your hyperparams for the generation
        """

        body = self.body_compose(
            config,
            prompt,
            negative_prompt=neg,
            init_image=image,
            mask_image=mask
        )

        images = self.request('inpaint', body)
        return images
