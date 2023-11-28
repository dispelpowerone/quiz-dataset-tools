import os, shutil


class Images:
    INDEX_FILE = "index.ts"

    def __init__(self, source_dir, dest_dir):
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.index = {}

    def put(self, name: str, filename: str | None) -> None:
        # If image has already added
        if name in self.index:
            return

        dest_filename = None
        if filename:
            assert filename.endswith(".png")
            source_path = os.path.join(self.source_dir, filename)
            source_filename = os.path.basename(source_path)

            dest_filename = f"{name}.png"
            dest_path = os.path.join(self.dest_dir, dest_filename)

            assert not os.path.exists(dest_path)
            shutil.copyfile(source_path, dest_path)

        self.index[name] = dest_filename

    def save_index(self) -> None:
        index_parts: list[str] = []
        index_parts.append("export const Images = {")
        for name in sorted(self.index.keys()):
            filename = self.index[name]
            if filename:
                index_parts.append(
                    f"  '{name}': require('assets/img/questions/{filename}'),"
                )
            else:
                index_parts.append(f"  '{name}': null,")
        index_parts.append("};")

        index_path = os.path.join(self.dest_dir, Images.INDEX_FILE)
        with open(index_path, "w") as output:
            output.write("\n".join(index_parts))

    def clean(self):
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
        index_file_path = os.path.join(self.dest_dir, Images.INDEX_FILE)
        if os.path.exists(index_file_path):
            os.unlink(index_file_path)
