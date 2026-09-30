from .prompt_format import format_prompt_json
from .pose_reference import reference_image, camera_preview
import numpy as np
import torch

from .pose_core import MODES, build_prompt, read_scene, render_pose


class FisherPoseStudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "output_mode": (MODES, {"default": MODES[0]}),
            "width": ("INT", {"default": 768, "min": 64, "max": 4096, "step": 8}),
            "height": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 8}),
            "extra_prompt": ("STRING", {"default": "", "multiline": True}),
            "scene_json": ("STRING", {"default": "{}", "multiline": True}),
        }}

    RETURN_TYPES = ("STRING", "IMAGE", "IMAGE")
    RETURN_NAMES = ("prompt", "mannequin_pose_image", "camera_preview")
    FUNCTION = "generate"
    CATEGORY = "Fisher/Pose & Camera"
    DESCRIPTION = "1–3 people with independent poses and positions sharing one camera. Connect the prompt to prompt, the framed mannequin pose image to image_2 and the source image directly to image_1. In camera-only mode, leave the pose image output unconnected."

    def generate(self, output_mode, width, height, extra_prompt, scene_json):
        state = read_scene(scene_json)
        if not state["people"]:
            output_mode = "仅视角"
        prompt = build_prompt(state, output_mode, extra_prompt)
        prompt = format_prompt_json(prompt, state, output_mode, width, height)
        image = (reference_image(scene_json) if output_mode != "仅视角" else render_pose(state, 1536, 864))
        tensor = torch.from_numpy(np.asarray(image).astype(np.float32) / 255.0).unsqueeze(0)
        preview=torch.from_numpy(np.asarray(camera_preview(scene_json)).astype(np.float32)/255).unsqueeze(0)
        return {"ui": {"fisher_prompt": [prompt]}, "result": (prompt, tensor, preview)}
