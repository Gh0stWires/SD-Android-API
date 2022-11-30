import BaseAsyncClass
from diffusers import StableDiffusionPipeline
import tokens
import torch
from flask_sqlalchemy import SQLAlchemy
from models import Image

class DiffusionUtils():

    def __init__(self):
        self.pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", use_auth_token=tokens.HFTOKEN).to("cuda")
        self.pipe.safety_checker = dummy_checker

    def make(self,prompt, num_of_images, user, token, db_commit_callback):
        files = []
        OUTDIR = 'generated/'
        PROMPT = prompt
        NUM_ITERS = num_of_images
        SEED = 0 
        SCALE = 10.5 
        WIDTH = 512 
        HEIGHT = 512
        STEPS = 250
        ORIG_SEED = SEED
        generator = torch.Generator(device="cuda")
        latents = None
        seeds = []
        print(prompt)
        for i in range(NUM_ITERS):
            torch.cuda.empty_cache()
            seed = generator.seed()
            seeds.append(seed)
            generator = generator.manual_seed(seed)
        
            image_latents = torch.randn((1, self.pipe.unet.in_channels, HEIGHT // 8, WIDTH // 8), generator = generator, device = "cuda")
            latents = image_latents if latents is None else torch.cat((latents, image_latents))
            image = self.pipe(PROMPT, num_inference_steps=STEPS, width=int(WIDTH), height=int(HEIGHT), guidance_scale=SCALE,
                        generator=generator, latents = latents)["sample"][0]
            uri = f'{OUTDIR}/{str(0)}_scale_{SCALE}_steps_{STEPS}_seed_{seeds[i]}.png'
            image.save(uri)
            files.append(uri)
            db_commit_callback(uri, PROMPT, user, token)
            torch.cuda.empty_cache()
        return files

def dummy_checker(images, **kwargs): return images, False