import torch
from diffusers import DiffusionPipeline

class RenderEngine:
    def __init__(self):
        self.pipe = None

    def load_pipeline(self, path):
        self.pipe = DiffusionPipeline.from_pretrained(
            path,
            torch_dtype=torch.float16
        )

        self.pipe.enable_sequential_cpu_offload()

    def generate(self, prompt):
        image = self.pipe(
            prompt=prompt,
            num_inference_steps=25
        ).images[0]

        return image
