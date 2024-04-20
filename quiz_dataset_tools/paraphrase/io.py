import dataclasses
import json
import os
from quiz_dataset_tools.paraphrase.types import ParaphrasedQuestion


# Chunk templ parameters:
#  {index} - chunk index
def save_questions_chunked(
    questions: list[ParaphrasedQuestion], data_dir: str, chunk_templ: str
) -> None:
    chunk_size = 20
    chunk_index = 1
    while True:
        i = (chunk_index - 1) * chunk_size
        if i >= len(questions):
            break

        chunk_data = [dataclasses.asdict(e) for e in questions[i : i + chunk_size]]
        chunk_index += 1

        out_file = chunk_templ.format(index=chunk_index)

        chunk_file_path = f"{data_dir}/{out_file}"
        with open(chunk_file_path, "w") as output:
            json.dump(chunk_data, output, indent=4)


def load_questions_chunked(
    data_dir: str, chunk_templ: str
) -> list[ParaphrasedQuestion]:
    result: list[ParaphrasedQuestion] = []
    chunk_index = 0
    while True:
        chunk_index += 1
        input_file = chunk_templ.format(index=chunk_index)
        input_path = f"{data_dir}/{input_file}"
        if not os.path.isfile(input_path):
            print(f"No file at {input_path}, stop reading")
            break
        print(f"Read data file: {input_path}")
        result.extend(_parse_questions_json(input_path))
    print(f"Loaded {len(result)} uniq pairs")
    return result


def _parse_questions_json(file_path: str) -> list[ParaphrasedQuestion]:
    result: list[ParaphrasedQuestion] = []
    with open(file_path, "r") as fd:
        file_data = json.load(fd)
        for entry in file_data:
            try:
                result.append(ParaphrasedQuestion.from_dict(entry))
            except:
                print(entry)
                raise
    return result
