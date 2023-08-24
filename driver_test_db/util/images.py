import os, shutil


class Images:
    def __init__(self, source_dir, dest_dir):
        self.source_dir = source_dir
        self.dest_dir = dest_dir

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

    def put(self, filename):
        if not filename:
            return

        source_path = os.path.join(self.source_dir, filename)
        source_filename = os.path.basename(source_path)
        dest_path = os.path.join(self.dest_dir, source_filename)

        if os.path.exists(dest_path):
            return

        shutil.copyfile(source_path, dest_path)
