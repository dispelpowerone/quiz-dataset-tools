import base64
import os
from PIL import Image
from io import BytesIO


def convert_png_to_webp(input_file: str, output_file: str, quality: int = 90) -> None:
    """
    Converts a PNG image to WEBP format.
    Args:
        input_file (str): Path to the PNG file.
        output_file (str): Path to save the WEBP file.
        quality (int): Quality of the output WEBP image (1-100).
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File {input_file} not found.")
    if not input_file.lower().endswith(".png"):
        raise ValueError("Input file must be a PNG file.")
    if os.path.exists(output_file):
        raise ValueError(f"Output file {output_file} already exists.")
    if not output_file.lower().endswith(".webp"):
        raise ValueError("Output file must be a WEBP file.")

    # Open the input PNG file
    with Image.open(input_file) as img:
        # Convert the image to RGB if it has an alpha channel (RGBA)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        # Save the image as WEBP
        img.save(output_file, "webp", quality=quality)


def load_image_as_base64(image_path: str) -> str:
    with Image.open(image_path) as img:
        return _pil_to_base64_jpeg(img)


def _pil_to_base64_jpeg(pil_image) -> str:
    """
    Converts a PIL Image object to a Base64 encoded string.
    Args:
        pil_image (PIL.Image.Image): The PIL Image object to convert.
    Returns:
        str: The Base64 encoded string of the image.
    """
    buffered = BytesIO()
    rgb_image = pil_image.convert("RGB")
    rgb_image.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return base64_string
