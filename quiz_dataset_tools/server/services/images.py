import glob
import os
import re
import shutil
from PIL import Image
from quiz_dataset_tools.server.services.database import DatabaseService

IMAGE_WIDTH = 750
IMAGE_HEIGHT = 300


class ImagesService:
    def __init__(self, database_service: DatabaseService):
        self.database_service = database_service

    def upload_question_image(
        self, domain: str, question_id: int, temp_image: str
    ) -> tuple[str, str]:
        is_valid, error = self.check_question_image(temp_image)
        if not is_valid:
            return "", error
        image, error = self.save_question_image(domain, question_id, temp_image)
        return image, ""

    def check_question_image(self, temp_image: str) -> tuple[bool, str]:
        try:
            # Check file type and resolution
            with Image.open(temp_image) as img:
                if img.format != "PNG":
                    return False, "Not a PNG file"
                width, height = img.size
                print(f"File is a PNG with resolution: {width}x{height}")
                if width != IMAGE_WIDTH or height != IMAGE_HEIGHT:
                    return False, f"Expected resolution {IMAGE_WIDTH}x{IMAGE_HEIGHT}"
        except IOError:
            return False, "Not a valid image file"
        return True, ""

    def save_question_image(
        self, domain: str, question_id: int, temp_image: str
    ) -> tuple[str, str]:
        image_dir = self.database_service.get_data_dir(domain) + "/images/"
        image_mask = f"{image_dir}/{question_id}-*.png"
        image_index = 1
        # Check for other versions
        files = glob.glob(image_mask)
        files.sort()
        if files:
            match = re.search(r"-(\d+)", files[-1])
            if not match:
                return "", f"Can't find image index: {files[-1]}"
            image_index = int(match.group(1)) + 1
        # Save
        image_filename = f"{question_id}-{image_index}.png"
        image_path = f"{image_dir}/{image_filename}"
        try:
            shutil.move(temp_image, image_path)
        except IOError:
            return "", f"Can't move temp image {temp_image} to {image_path}"
        return image_filename, ""
