import glob
from bs4 import BeautifulSoup
from typing import Any
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.data import Test, Question, Answer
from quiz_dataset_tools.parser.parser import Parser


class TildaParser(Parser):
    def __init__(self, project_path: str):
        self.project_path = project_path

    def get_tests(self) -> list[Test]:
        return self._load_tests()

    def _load_tests(self) -> list[Test]:
        test_obj_list = []
        pages = glob.glob(f"{self.project_path}/page*")
        for page_index, page_path in enumerate(sorted(pages)):
            test_id = page_index + 1
            test_obj_list.append(self._load_test(test_id, page_path))
        return test_obj_list

    def _load_test(self, test_id: int, page_path: str) -> Test:
        with open(page_path) as fd:
            soup = BeautifulSoup(fd, "html.parser")
            return Test(
                title=self._make_text(f"Test {test_id}"),
                questions=self._load_questions(soup.find_all("div", "t806__question")),
            )

    def _load_questions(self, questions_soup: Any) -> list[Question]:
        question_obj_list = []
        for question_index, question in enumerate(questions_soup):
            question_id = question_index + 1
            try:
                question_obj_list.append(self._load_question(question_id, question))
            except:
                print(f"Bad question: {question}")
        return question_obj_list

    def _load_question(self, question_id: int, question_soup: Any) -> Question:
        question_text = question_soup.find("div", "t806__quest-text").text
        question_image = question_soup.find("div", "t806__quest-img").find("img")[
            "data-original"
        ]
        question_answers = question_soup.find("div", "t806__answers")
        return Question(
            orig_id=str(question_id),
            text=self._make_text(question_text),
            answers=self._load_answers(question_answers),
            image=f"{self.project_path}/{question_image}",
        )

    def _load_answers(self, answers_soup: Any) -> list[Answer]:
        right_answer_id = int(answers_soup["data-right-answer"])
        answer_obj_list = []
        for answer in answers_soup:
            answer_id = int(answer["data-answer-id"])
            answer_text = answer.find("span", "t806__answer-text_wrap").text
            answer_obj_list.append(
                Answer(
                    text=self._make_text(answer_text),
                    is_right_answer=(answer_id == right_answer_id),
                )
            )
        return answer_obj_list

    def _make_text(self, text: str) -> TextLocalizations:
        text_localizations = TextLocalizations()
        text_localizations.set(Language.EN, text)
        return text_localizations
