import os, shutil
from enum import Enum
from quiz_dataset_tools.util.fs import prepare_output_dir


class MediaType(Enum):
    IMAGE = 1
    AUDIO = 2


class MediaIndex:
    INDEX_FILE = "index.ts"
    TYPE_TO_ASSETS_DIR = {
        MediaType.IMAGE: "assets/img/questions",
        MediaType.AUDIO: "assets/audio/questions",
    }
    TYPE_TO_ASSETS_OBJ_NAME = {
        MediaType.IMAGE: "Images",
        MediaType.AUDIO: "Audio",
    }
    TYPE_TO_FILE_TYPE = {
        MediaType.IMAGE: "png",
        MediaType.AUDIO: "mp3",
    }

    def __init__(
        self,
        media_type: MediaType,
        source_dir,
        dest_dir,
        preserve_file_names: bool = True,
    ):
        self.media_type = media_type
        self.file_type = MediaIndex.TYPE_TO_FILE_TYPE[media_type]
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.preserve_file_names = preserve_file_names
        self.index: dict[str, str | None] = {}
        self.inverted_index: dict[str, str] = {}

    def put(self, name: str, filename: str | None) -> None:
        # If media has already added for a given key
        if name in self.index:
            return
        # Format final filename
        if not filename:
            self.index[name] = None
            return
        dest_filename = self.inverted_index.get(filename)
        if not dest_filename:
            if self.preserve_file_names:
                dest_filename = filename
            else:
                dest_filename = f"{name}.{self.file_type}"
            self._copy_data(filename, dest_filename)
            self.inverted_index[filename] = dest_filename
        self.index[name] = dest_filename

    def save_index(self) -> None:
        assets_dir = MediaIndex.TYPE_TO_ASSETS_DIR[self.media_type]
        assets_obj_name = MediaIndex.TYPE_TO_ASSETS_OBJ_NAME[self.media_type]
        index_parts: list[str] = []
        index_parts.append(f"export const {assets_obj_name} = {{")
        for name in sorted(self.index.keys()):
            filename = self.index[name]
            if filename:
                index_parts.append(f"  '{name}': require('{assets_dir}/{filename}'),")
            else:
                index_parts.append(f"  '{name}': null,")
        index_parts.append("};")

        index_path = os.path.join(self.dest_dir, MediaIndex.INDEX_FILE)
        with open(index_path, "w") as output:
            output.write("\n".join(index_parts))

    def clean(self) -> None:
        prepare_output_dir(self.dest_dir)
        self.index = {}
        self.inverted_index = {}

    def _copy_data(self, src_file: str, dest_file: str) -> None:
        assert src_file.endswith(f".{self.file_type}")
        source_path = os.path.join(self.source_dir, src_file)
        dest_path = os.path.join(self.dest_dir, dest_file)
        if not os.path.exists(dest_path):
            shutil.copyfile(source_path, dest_path, follow_symlinks=True)
