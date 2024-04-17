import os, shutil
from enum import Enum


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

    def __init__(self, media_type: MediaType, source_dir, dest_dir):
        self.media_type = media_type
        self.file_type = MediaIndex.TYPE_TO_FILE_TYPE[media_type]
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.index: dict[str, str | None] = {}

    def put(self, name: str, filename: str | None) -> None:
        # If media has already added for a given key
        if name in self.index:
            return
        # Copy to the dest dir
        if filename:
            self._copy_data(filename)
        self.index[name] = filename

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
        for filename in os.listdir(self.dest_dir):
            file_path = os.path.join(self.dest_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))
        self.index = {}
        index_file_path = os.path.join(self.dest_dir, MediaIndex.INDEX_FILE)
        if os.path.exists(index_file_path):
            os.unlink(index_file_path)

    def _copy_data(self, filename: str) -> None:
        assert filename.endswith(f".{self.file_type}")
        source_path = os.path.join(self.source_dir, filename)
        dest_path = os.path.join(self.dest_dir, filename)
        if not os.path.exists(dest_path):
            shutil.copyfile(source_path, dest_path, follow_symlinks=True)
