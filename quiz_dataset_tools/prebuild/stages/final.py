import os, shutil
from quiz_dataset_tools.util.fs import prepare_output_dir
from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage
from quiz_dataset_tools.prebuild.types import PrebuildTest, PrebuildQuestion
from quiz_dataset_tools.prebuild.dbase import PrebuildDBase


class FinalStage(DataUpdateBaseStage):
    def __init__(self, data_path: str, output_dir: str):
        self.data_images_dir = f"{data_path}/images"
        self.output_data_dir = f"{output_dir}/data"
        self.images_dir = f"{self.output_data_dir}/images"
        self.dbase = PrebuildDBase(data_dir=self.output_data_dir)

    def setup(self):
        prepare_output_dir(self.output_data_dir)
        prepare_output_dir(self.images_dir)
        self.dbase.bootstrap()

    def update_test(self, test: PrebuildTest) -> None:
        self.dbase.add_test(test)

    def update_question(self, question: PrebuildQuestion) -> None:
        self.dbase.add_question(question)
        if question.image:
            self._copy_image(question.image)

    def _copy_image(self, image_file: str):
        source_path = os.path.join(self.data_images_dir, image_file)
        dest_path = os.path.join(self.images_dir, image_file)
        if not os.path.exists(dest_path):
            shutil.copyfile(source_path, dest_path, follow_symlinks=True)
