from torchvision.models import EfficientNet_V2_S_Weights
from PIL import Image

def get_preprocessing_transform():
    # Use the official pretrained weights transforms
    weights = EfficientNet_V2_S_Weights.DEFAULT
    return weights.transforms()

def preprocess_image(image: Image.Image):
    transform = get_preprocessing_transform()
    if image.mode != "RGB":
        image = image.convert("RGB")
    tensor = transform(image)
    return tensor.unsqueeze(0)  # Add batch dimension
