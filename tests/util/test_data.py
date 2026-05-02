import unittest
from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)
from quiz_dataset_tools.util.data import Answer, Question, Test


class TestAnswerTransform(unittest.TestCase):
    def test_transform_texts(self):
        text = TextLocalizations()
        text.set(Language.EN, "  answer  ")
        answer = Answer(text=text, is_right_answer=True, orig_id=5)

        result = answer.transform_texts(lambda t: t.transform(str.strip))
        self.assertEqual(result.text.get(Language.EN).content, "answer")
        self.assertTrue(result.is_right_answer)
        self.assertEqual(result.orig_id, 5)

    def test_transform_preserves_is_right_answer(self):
        text = TextLocalizations()
        text.set(Language.EN, "wrong")
        answer = Answer(text=text, is_right_answer=False)

        result = answer.transform_texts(lambda t: t)
        self.assertFalse(result.is_right_answer)


class TestQuestionTransform(unittest.TestCase):
    def setUp(self):
        q_text = TextLocalizations()
        q_text.set(Language.EN, "  question  ")
        a_text = TextLocalizations()
        a_text.set(Language.EN, "  answer  ")
        self.question = Question(
            text=q_text,
            answers=[Answer(text=a_text, is_right_answer=True)],
            orig_id=10,
            image="img.png",
            audio="audio.mp3",
        )

    def test_transform_texts_applies_to_question_and_answers(self):
        result = self.question.transform_texts(lambda t: t.transform(str.strip))
        self.assertEqual(result.text.get(Language.EN).content, "question")
        self.assertEqual(result.answers[0].text.get(Language.EN).content, "answer")

    def test_transform_texts_preserves_metadata(self):
        result = self.question.transform_texts(lambda t: t)
        self.assertEqual(result.orig_id, 10)
        self.assertEqual(result.image, "img.png")
        self.assertEqual(result.audio, "audio.mp3")

    def test_transform_question_text_only(self):
        result = self.question.transform_question_text(lambda t: t.transform(str.strip))
        self.assertEqual(result.text.get(Language.EN).content, "question")
        # answers remain unchanged (same object)
        self.assertEqual(result.answers[0].text.get(Language.EN).content, "  answer  ")

    def test_transform_question_text_preserves_metadata(self):
        result = self.question.transform_question_text(lambda t: t)
        self.assertEqual(result.orig_id, 10)
        self.assertEqual(result.image, "img.png")
        self.assertEqual(result.audio, "audio.mp3")


class TestTestTransform(unittest.TestCase):
    def setUp(self):
        title = TextLocalizations()
        title.set(Language.EN, "Test Title")
        q_text = TextLocalizations()
        q_text.set(Language.EN, "  q1  ")
        a_text = TextLocalizations()
        a_text.set(Language.EN, "  a1  ")
        self.test = Test(
            title=title,
            questions=[
                Question(
                    text=q_text,
                    answers=[Answer(text=a_text, is_right_answer=False)],
                )
            ],
            position=1,
            orig_id=99,
        )

    def test_transform_texts(self):
        result = self.test.transform_texts(lambda t: t.transform(str.strip))
        self.assertEqual(result.questions[0].text.get(Language.EN).content, "q1")
        self.assertEqual(
            result.questions[0].answers[0].text.get(Language.EN).content, "a1"
        )

    def test_transform_texts_preserves_title(self):
        result = self.test.transform_texts(lambda t: t.transform(str.strip))
        # title is not transformed by transform_texts
        self.assertEqual(result.title.get(Language.EN).content, "Test Title")

    def test_transform_texts_preserves_metadata(self):
        result = self.test.transform_texts(lambda t: t)
        self.assertEqual(result.position, 1)
        self.assertEqual(result.orig_id, 99)

    def test_transform_question_texts(self):
        result = self.test.transform_question_texts(lambda t: t.transform(str.strip))
        self.assertEqual(result.questions[0].text.get(Language.EN).content, "q1")
        # answers not transformed
        self.assertEqual(
            result.questions[0].answers[0].text.get(Language.EN).content, "  a1  "
        )
