"""Free-pose mode: VNCCS Pose Studio LoRA convention for Qwen Image 2.1.

The VNCCS_QI2_PoseStudio LoRA was trained with the mannequin render as image1,
the character photo as image2 and the fixed instruction below, so this node
keeps exactly that order and wording instead of our long Chinese edit prompt.
"""
import numpy as np
import torch

from .pose_reference import reference_image

VNCCS_INSTRUCTION = "Draw character from image2"


def free_pose_prompt(extra=""):
    lines = [VNCCS_INSTRUCTION] + [line.strip() for line in str(extra or "").splitlines()]
    return "\n".join(line for line in lines if line)


def mannequin_tensor(pose_json):
    # The mannequin keeps the size chosen in the editor; the node's width/height only set the output latent.
    return torch.from_numpy(np.asarray(reference_image(pose_json)).astype(np.float32) / 255).unsqueeze(0)


class FisherQwenFreePose:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "clip": ("CLIP",), "vae": ("VAE",), "reference_image": ("IMAGE",),
            "width": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 16}),
            "height": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 16}),
            "reference_resolution": ("INT", {"default": 1024, "min": 256, "max": 2048, "step": 32}),
            "extra_prompt": ("STRING", {"default": "", "multiline": True}),
            "pose_json": ("STRING", {"default": "{}", "multiline": True}),
        }}

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "LATENT", "STRING", "IMAGE")
    RETURN_NAMES = ("positive", "negative", "latent", "actual_prompt", "mannequin_pose_image")
    FUNCTION = "encode"
    CATEGORY = "Fisher/Pose & Camera"
    DESCRIPTION = "Qwen Image 2.1 free pose (single person). For the VNCCS_QI2_PoseStudio LoRA: the mannequin image is image1, the person image is image2 and the prompt is fixed to Draw character from image2. The mannequin size is set in the editor; the node's width/height only set the output size (a resolution node can be connected) and need not match it."

    def encode(self, clip, vae, reference_image, width, height, reference_resolution, extra_prompt, pose_json):
        if width % 16 or height % 16:
            raise ValueError("Qwen output width and height must be multiples of 16. Adjust the node's width/height.")
        if reference_image.ndim != 4 or reference_image.shape[0] != 1:
            raise ValueError("Free pose accepts a single person image. Do not connect an image batch.")
        mannequin = mannequin_tensor(pose_json)
        prompt = free_pose_prompt(extra_prompt)
        try:
            from comfy_extras.nodes_qwen import TextEncodeQwenImage21
        except ImportError as error:
            raise RuntimeError("This node requires a newer ComfyUI that includes TextEncodeQwenImage21.") from error
        result = TextEncodeQwenImage21.execute(clip=clip, prompt=prompt, negative_prompt="", vae=vae,
                    resolution=reference_resolution, images={"image_1": mannequin, "image_2": reference_image})
        positive, negative, encoded_latent = result.result
        # Output size comes from the node, independent of the mannequin (the encoder would size it from image1).
        latent = {"samples": encoded_latent["samples"].new_zeros((1, 64, height // 16, width // 16))}
        return {"ui": {"fisher_prompt": [prompt]}, "result": (positive, negative, latent, prompt, mannequin)}
