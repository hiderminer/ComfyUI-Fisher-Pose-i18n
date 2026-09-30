"""Decode the editor-rendered shooting-frame mannequin reference."""
import base64
import io
import json
from PIL import Image, ImageDraw


def reference_image(scene_json, key='poseReference'):
    data=json.loads(scene_json or '{}')
    encoded=data.get(key,'')
    if not encoded:
        raise ValueError('Open the editor and click "Apply to node" to create the mannequin reference image.')
    prefix='data:image/png;base64,'
    if not isinstance(encoded,str) or not encoded.startswith(prefix) or len(encoded)>32_000_000:
        raise ValueError('The mannequin reference data is invalid. Apply the editor again.')
    image=Image.open(io.BytesIO(base64.b64decode(encoded[len(prefix):],validate=True)))
    if not all((1 if key=='cameraPreview' else 64) <= value <= 4096 for value in image.size):
        raise ValueError('The mannequin reference must be 64–4096 pixels on each side. Apply the editor again.')
    return image.convert('RGB')


def camera_preview(scene_json):
    data=json.loads(scene_json or '{}')
    if data.get('cameraPreview'):
        return reference_image(scene_json, 'cameraPreview')
    # This output is independent of the model's pose reference. Legacy captures
    # intentionally omit the cube, so never substitute them for the preview.
    image = Image.new('RGB', (768, 432), (239, 242, 246))
    draw = ImageDraw.Draw(image)
    draw.text((48, 176), 'Camera preview needs refreshing.', fill=(35, 48, 68), font_size=26)
    draw.text((48, 224), 'Reload ComfyUI, open the editor, then click Apply.', fill=(70, 85, 105), font_size=22)
    return image
