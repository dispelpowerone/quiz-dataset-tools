import os
import glob
from typing import TypeVar, Type
from dataclasses_json import DataClassJsonMixin


def prepare_output_dir(dir_name: str):
    os.makedirs(dir_name, exist_ok=True)
    file_paths = glob.glob(f"{dir_name}/*")
    for file_path in file_paths:
        os.remove(file_path)


T = TypeVar("T", bound=DataClassJsonMixin)


def dump_list(cls: Type[T], data: list[T], output_dir: str, chunk_size: int) -> None:
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


def load_list(cls: Type[T], source_dir: str) -> list[T]:
    if not os.path.isdir(source_dir):
        raise Exception(f"No source directory found {source_dir}")
    file_paths = list_partial_files(f"{source_dir}/out.__INDEX__.json")
    data = []
    for file_path in file_paths:
        with open(file_path, "r") as fd:
            data.extend(cls.schema().loads(fd.read(), many=True))
    return data


def list_partial_files(template: str) -> list[str]:
    placeholder = "__INDEX__"
    # Build list of files
    index = 1
    files_list: list[str] = []
    while True:
        file_name = template.replace(placeholder, str(index))
        if not os.path.isfile(file_name):
            break
        files_list.append(file_name)
        index += 1
    # Check the list
    glob_paths = glob.glob(template.replace(placeholder, "*"))
    if len(files_list) != len(glob_paths):
        raise Exception(f"Broken files list: {files_list} != {glob_paths}")
    return files_list
