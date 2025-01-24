import os
import torch
from PIL import Image
import numpy as np

class FL_API_ImageSaver:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "job_id": ("STRING",),
                "category": ("STRING",),
                "base_output_dir": ("STRING", {"default": "/absolute/path/to/output"}),
                "image_format": ("STRING", {
                    "default": "png",
                    "choices": ["png", "jpg", "jpeg", "webp"],
                }),
                "image_quality": ("INT", {
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("saved_path", "job_id", "category")
    FUNCTION = "save_categorized_image"
    CATEGORY = "🏵️Fill Nodes/API Tools"
    OUTPUT_NODE = True

    def save_categorized_image(self,
                             image: torch.Tensor,
                             job_id: str,
                             category: str,
                             base_output_dir: str,
                             image_format: str = "png",
                             image_quality: int = 100) -> tuple:
        try:
            # Ensure base directory exists
            if not os.path.exists(base_output_dir):
                os.makedirs(base_output_dir)

            # Create category subdirectory
            category_dir = os.path.join(base_output_dir, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir)

            # Prepare image filename
            filename = f"{job_id}.{image_format}"
            full_path = os.path.join(category_dir, filename)

            # Convert tensor to PIL Image
            i = 255. * image.cpu().numpy().squeeze()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # Save image with appropriate format and quality
            if image_format.lower() in ['jpg', 'jpeg']:
                img.save(full_path, 'JPEG', quality=image_quality)
            elif image_format.lower() == 'webp':
                img.save(full_path, 'WEBP', quality=image_quality)
            else:  # PNG
                img.save(full_path, 'PNG')

            print(f"Image saved successfully: {full_path}")
            return (full_path, job_id, category)

        except Exception as e:
            raise ValueError(f"Error saving image: {str(e)}")

    @classmethod
    def IS_CHANGED(cls, image, job_id, category, base_output_dir, image_format, image_quality):
        return float("NaN")