import os
import glob
from typing import TypeVar


def prepare_output_dir(dir_name: str):
    os.makedirs(dir_name, exist_ok=True)
    file_paths = glob.glob(f"{dir_name}/*")
    for file_path in file_paths:
        os.remove(file_path)


T = TypeVar("T")


def dump_list(cls: T, data: list[T], output_dir: str, chunk_size: int) -> None:
    prepare_output_dir(output_dir)
    chunk_name_templ = output_dir + "/out.{index}.json"
    chunk_index = 1
    while True:
        i = (chunk_index - 1) * chunk_size
        if i >= len(data):
            break
        chunk_data = cls.schema().dumps(
            data[i : i + chunk_size], many=True, indent=2, ensure_ascii=False
        )
        chunk_file = chunk_name_templ.format(index=chunk_index)
        chunk_index += 1
        with open(chunk_file, "w") as fd:
            fd.write(chunk_data)


def load_list(cls: T, source_dir: str) -> list[T] | None:
    if not os.path.isdir(source_dir):
        return None
    data = []
    file_paths = glob.glob(f"{source_dir}/out.*.json")
    for file_path in file_paths:
        with open(file_path, "r") as fd:
            data.extend(cls.schema().loads(fd.read(), many=True))
    return data
