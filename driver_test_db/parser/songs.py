import json
from typing import Any
from driver_test_db.parser.parser import Parser
from driver_test_db.util.data import Test, Question, Answer
from driver_test_db.util.language import Language, TextLocalizations


SongType = dict[str, Any]


class SongsParser(Parser):
    def __init__(self, data_path: str):
        self.data_path = data_path

    def get_tests(self) -> list[Test]:
        return self._make_tests(self._load_index())

    def _load_index(self) -> list[SongType]:
        with open(f"{self.data_path}/index.json") as fd:
            return json.load(fd)

    def _make_tests(self, songs: list[SongType]) -> list[Test]:
        questions_per_test = 15
        tests: list[Test] = []
        questions = []
        question_index = 0
        questions_total = (
            (len(songs) - 1) // questions_per_test + 1
        ) * questions_per_test
        for i in range(questions_total):
            song = songs[i % len(songs)]
            questions.append(self._make_question(song, i))
            if len(questions) == questions_per_test:
                tests.append(self._make_test(len(tests) + 1, questions))
                questions = []
        return tests

    def _make_test(self, test_id: int, questions: list[Question]) -> Test:
        return Test(
            title=self._make_text(f"Test {test_id}"),
            questions=questions,
        )

    def _make_question(self, song: SongType, song_index: int) -> Question:
        return Question(
            orig_id=self._make_id(song),
            text=self._make_text(song["question"]),
            answers=self._make_answers(song["answers"]),
            image=f"{song_index % 10 + 1}.png",
            audio=self._get_file_name(song["sample_file"]),
        )

    def _make_id(self, song: SongType) -> str:
        track_file_name = song["track_file"].split("/")[-1]
        return track_file_name[:-4]

    def _make_answers(self, answer_list: list[str]) -> list[Answer]:
        answers = []
        for i, answer in enumerate(answer_list):
            answers.append(
                Answer(
                    text=self._make_text(answer),
                    is_right_answer=(i == 0),
                )
            )
        return answers

    def _make_text(self, text: str) -> TextLocalizations:
        text_localizations = TextLocalizations()
        text_localizations.set(Language.EN, text.strip())
        return text_localizations

    def _get_file_name(self, path: str) -> str:
        return path.split("/")[-1]
