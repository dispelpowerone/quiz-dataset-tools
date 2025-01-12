from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.build.dbase import MainDBase


def check_prebuild_main_consistency(prebuild_dir: str, build_dir: str):
    prebuild_db = PrebuildDBase(prebuild_dir)
    main_db = MainDBase(build_dir)
    # Check that QuestionId are equal
    prebuild_questions = prebuild_db.get_questions()
    prebuild_questions_flat = []
    for question in prebuild_questions:
        for answer in question.answers:
            prebuild_questions_flat.append(
                (
                    question.test_id,
                    question.question_id,
                    question.text.localizations.EN,
                    answer.text.localizations.EN,
                )
            )
    main_questions = main_db.get_questions()
    main_questions_flat = []
    for question in main_questions:
        for answer in question.answers:
            main_questions_flat.append(
                (
                    question.test_id,
                    question.question_id,
                    question.text.localizations.EN,
                    answer.text.localizations.EN,
                )
            )
    prebuild_questions_flat = sorted(prebuild_questions_flat)
    main_questions_flat = sorted(main_questions_flat)
    assert len(prebuild_questions_flat) == len(main_questions_flat)
    for i, val in enumerate(prebuild_questions_flat):
        assert val == main_questions_flat[i]
