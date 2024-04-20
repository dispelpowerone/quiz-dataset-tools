import sqlite3
from dataclasses import dataclass
from quiz_dataset_tools.util.data import Question, Answer, Test
from quiz_dataset_tools.util.language import Language, TextLocalizations


@dataclass
class GQuestion:
    id: int
    description: str
    image_name: str
    correct_answer: int


@dataclass
class GAnswer:
    id: int
    text: str


def load_ny_tests() -> list[Test]:
    test_size = 15
    tests: list[Test] = []
    questions = load_state_questions(33)
    for i in range(0, len(questions), test_size):
        tests.append(
            Test(
                title=_make_text(f"Test {len(tests) + 1}"),
                questions=questions[i : i + test_size],
            )
        )
    return tests


def load_state_questions(state_id: int):
    dbase_path = "data/usa/tests_US.db"
    cursor = sqlite3.connect(dbase_path)
    cursor.execute("pragma encoding=UTF8")

    questions = []
    g_questions = _load_state_questions(cursor, state_id)
    for g_question in g_questions:
        g_answers = _load_question_answers(cursor, g_question.id)
        questions.append(_make_question(g_question, g_answers))
    return questions


def _load_state_questions(cursor, state_id: int):
    query = f"""
select distinct
  q.Id
  , q.description
  , q.imageName
  , correctAnswer
from question q
left join test_question tq on tq.q_Id = q.Id
left join state_test st on st.t_Id = tq.t_Id
left join test t on t.Id = st.t_Id
where st.s_Id = {state_id}
    and t.type < 20
    """
    res = cursor.execute(query)
    questions = []
    for row in res.fetchall():
        questions.append(
            GQuestion(
                id=row[0],
                description=row[1],
                image_name=row[2],
                correct_answer=row[3],
            )
        )
    return questions


def _load_question_answers(cursor, question_id: int):
    query = f"""
select
    a.Id
  , a.text
from answer a
left join question_answer qa on qa.a_Id = a.Id
where qa.q_Id = {question_id}
    """
    res = cursor.execute(query)
    answers = []
    for row in res.fetchall():
        answers.append(
            GAnswer(
                id=row[0],
                text=row[1],
            )
        )
    return answers


def _make_question(g_question: GQuestion, g_answers: list[GAnswer]) -> Question:
    answers = []
    for g_answer in g_answers:
        answers.append(
            Answer(
                text=_make_text(g_answer.text),
                is_right_answer=(g_answer.id == g_question.correct_answer),
            )
        )
    image_png = g_question.image_name.replace(".png", "_Normal.png").replace(
        ".jpg", "_Normal.png"
    )
    return Question(
        orig_id=str(g_question.id),
        text=_make_text(g_question.description),
        image=image_png,
        answers=answers,
    )


def _make_text(g_text: str) -> TextLocalizations:
    text = TextLocalizations()
    text.set(Language.EN, g_text)
    return text
