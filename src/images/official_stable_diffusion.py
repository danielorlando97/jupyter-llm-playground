# Reference  https://stablediffusionapi.com/

import json
import os
from dotenv import load_dotenv
import requests
from dataclasses import dataclass
from typing import Union, Literal
import time
from base64 import b64decode

load_dotenv()

Model = Union[
    None,
    Literal['midjourney'],
]

models = [
    "stable-diffusion-v1-5",
    "stable-diffusion-xl-beta-v2-2-2",
    "stable-diffusion-512-v2-1",
    "stable-diffusion-768-v2-1",
]

samplers = [
    'K_DPMPP_2M',
    'DDIM',
    'DDPM',
    'K_DPMPP_2S_ANCESTRAL',
    'K_DPM_2',
    'K_DPM_2_ANCESTRAL',
    'K_EULER',
    'K_EULER_ANCESTRAL',
    'K_HEUN',
    'K_LMS',
]


styles = [
    'comic-book',
    '3d-model',
    'analog-film',
    'comic-book',
    'digital-art',
    'fantasy-art',
    'line-art',
    'low-poly',
    'modeling-compound',
    'neon-punk',
    'pixel-art',
    'tile-texture',
    'anime',
    'cinematic',
    'enhance',
    'isometric',
    'origami',
    'photographic',
]


@dataclass
class OficialStableDiffusionApiModelConfig:
    sampler: float = 'K_DPM_2_ANCESTRAL'
    steps: int = 50
    seed: int = 0
    cfg_scale: float = 15.0
    style_preset: str = 'comic-book'

    width: int = 512
    height: int = 512
    samples: int = 1

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
RETRY_LABEL = "......... The model say '{message}' but It's going retry 🦾"


def formatter(f):
    def ff(self, *arg, **kwd):
        result = f(self, *arg, **kwd)

        if result and hasattr(self, 'output_formatter'):
            return self.output_formatter(result)

        return result

    return ff


class OficialStableDiffusionApi:
    def __init__(self, model: Model = 'stable-diffusion-v1-5', save_seed=False, image_formatter=lambda p: p, prompt_suffix=None, retry_times=0) -> None:
        self.key = os.getenv("STABILITY_KEY")
        self.model_id = model
        self.save_seed = save_seed
        self.output_formatter = image_formatter
        self.prompt_suffix = prompt_suffix
        self.retry_times = retry_times

        self.base_url = f'https://api.stability.ai/v1/generation/{self.model_id}/'

        # print(INIT_LABEL.format(key=self.key))

    def body_compose(self, config: OficialStableDiffusionApiModelConfig, prompt, **info):
        body = {
            ** config,
            ** info,
            "text_prompts": prompt
        }

        if hasattr(self, 'seed'):
            body['seed'] = self.seed

        return body

    def request(self, tag, body, retry_times=None):

        if retry_times is None:
            retry_times = self.retry_times

        r = requests.post(
            self.base_url + tag,
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.key}"
            })

        res = r.json()
        try:
            res = res['artifacts'][0]
        except:
            print(body)
            raise Exception(res)

        # if res['status'] == 'failed':
        #     if retry_times > 0:
        #         print(RETRY_LABEL.format(message=res['messege']))
        #         return self.request(tag, body, retry_times - 1)

        #     print(ERROR_LABEL.format(message=res['messege']))
        #     return

        if self.save_seed and not hasattr(self, 'seed'):
            self.seed = res['seed']
            print(SAVED_SEED_LABEL.format(seed=self.seed))
        else:
            print(GENERATE_SEED_LABEL.format(seed=res['seed']))

        result = res

        # while result['status'] == 'processing':
        #     print(GENERATING_LABEL)
        #     time.sleep(5)
        #     result = requests.post(
        #         res['fetch_result'],
        #         data=json.dumps({'key': self.key}),
        #         headers={'Content-Type': 'application/json'}
        #     )

        #     result = result.json()

        return b64decode(result['base64'])

    @formatter
    def text2image(self, prompt, neg='', config: OficialStableDiffusionApiModelConfig = OficialStableDiffusionApiModelConfig()):
        """
        :param str prompt: Your Prompt 
        :param str neg: Items you don't want in the image 
        :param StableDiffusionApiModelConfig config: Your hyperparams for the generation
        """
        prompts = [
            {
                "text": prompt,
                "weight": 1
            },
        ]

        if neg != '':
            prompts.append({
                "text": neg,
                "weight": -1
            })

        body = self.body_compose(config, prompts)
        images = self.request('text-to-image', body)

        return images

    @formatter
    def image_by_multi_prompt(self, *prompts, config: OficialStableDiffusionApiModelConfig = OficialStableDiffusionApiModelConfig()):
        """
        :param str prompt: Your Prompt
        :param str neg: Items you don't want in the image
        :param StableDiffusionApiModelConfig config: Your hyperparams for the generation
        """

        prompt = []

        for p, w in prompts:
            prompt.append(
                {
                    "text": p,
                    "weight": w
                }
            )

        body = self.body_compose(config, prompt)
        images = self.request('text-to-image', body)

        return images
