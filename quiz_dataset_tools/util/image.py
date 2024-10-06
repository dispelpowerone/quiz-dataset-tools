import os
from PIL import Image


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
