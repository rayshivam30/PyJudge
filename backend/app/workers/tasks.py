from app.config.database import SessionLocal
from app.models.entities import Problem, Submission
from app.services.judge import run_problem_cases, update_leaderboard
from app.workers.celery_app import celery_app


@celery_app.task(name="judge_submission")
def judge_submission(submission_id: int) -> dict:
    db = SessionLocal()
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return {"error": "submission not found"}
        problem = db.get(Problem, submission.problem_id)
        if not problem:
            return {"error": "problem not found"}

        result = run_problem_cases(db, problem, submission.source_code, submission.language, hidden=True)
        submission.status = result.status
        submission.execution_time = result.execution_time
        submission.memory = result.memory
        db.add(submission)
        db.commit()
        db.refresh(submission)
        update_leaderboard(db, submission.user)
        return {"submission_id": submission.id, "status": submission.status.value}
    finally:
        db.close()
