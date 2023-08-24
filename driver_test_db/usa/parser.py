import sqlite3
from dataclasses import dataclass
from driver_test_db.util.data import Question, Answer, Test


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


def load_ny_tests():
    test_size = 15
    tests = list()
    questions = load_state_questions(33)
    for i in range(0, len(questions), test_size):
        tests.append(
            Test(
                title=f"Test {len(tests) + 1}",
                questions=questions[i : i + test_size],
            )
        )
    return tests


def load_state_questions(state_id: int):
    dbase_path = "usa/data/tests_US.db"
    cursor = sqlite3.connect(dbase_path)
    cursor.execute("pragma encoding=UTF8")

    questions = list()
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
where st.s_Id = {state_id}
    """
    res = cursor.execute(query)
    questions = list()
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
    answers = list()
    for row in res.fetchall():
        answers.append(
            GAnswer(
                id=row[0],
                text=row[1],
            )
        )
    return answers


def _make_question(g_question: GQuestion, g_answers: list[GAnswer]):
    answers = list()
    for g_answer in g_answers:
        answers.append(
            Answer(
                text=g_answer.text,
                is_right_answer=(g_answer.id == g_question.correct_answer),
            )
        )
    return Question(
        text=g_question.description,
        image=g_question.image_name,
        answers=answers,
    )
