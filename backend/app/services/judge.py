from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Leaderboard, Problem, Submission, TestCase, User, Verdict
from app.services.executor import Executor, JudgeExecution


def run_problem_cases(db: Session, problem: Problem, source_code: str, language: str, hidden: bool) -> JudgeExecution:
    cases = (
        db.query(TestCase)
        .filter(TestCase.problem_id == problem.id, TestCase.is_hidden.is_(hidden))
        .order_by(TestCase.id)
        .all()
    )
    if not cases:
        cases = db.query(TestCase).filter(TestCase.problem_id == problem.id).order_by(TestCase.id).all()
    executor = Executor()
    return executor.run_cases(
        language=language,
        source_code=source_code,
        cases=[(case.input, case.expected_output) for case in cases],
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
    )


def update_leaderboard(db: Session, user: User) -> None:
    total_submissions = db.query(Submission).filter(Submission.user_id == user.id).count()
    accepted_submissions = db.query(Submission).filter(
        Submission.user_id == user.id,
        Submission.status == Verdict.accepted,
    )
    solved_count = accepted_submissions.with_entities(func.count(func.distinct(Submission.problem_id))).scalar() or 0
    accepted_count = accepted_submissions.count()
    row = db.get(Leaderboard, user.id) or Leaderboard(user_id=user.id)
    row.problems_solved = solved_count
    row.score = solved_count * 100
    row.total_submissions = total_submissions
    row.acceptance_rate = (accepted_count / total_submissions * 100) if total_submissions else 0
    db.add(row)
    db.commit()
