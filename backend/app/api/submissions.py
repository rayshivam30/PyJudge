from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.config.database import get_db
from app.config.settings import get_settings
from app.models.entities import Problem, Submission, User, Verdict
from app.schemas.submission import ExecutionCaseResult, ExecutionResult, RunRequest, SubmissionRead, SubmitRequest
from app.services.judge import run_problem_cases, update_leaderboard

router = APIRouter(tags=["Submissions"])
settings = get_settings()


@router.post("/run", response_model=ExecutionResult)
def run_samples(payload: RunRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ExecutionResult:
    problem = db.get(Problem, payload.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    result = run_problem_cases(db, problem, payload.source_code, payload.language, hidden=False)
    return ExecutionResult(
        status=result.status,
        execution_time=result.execution_time,
        memory=result.memory,
        cases=[ExecutionCaseResult(**case.__dict__) for case in result.cases],
    )


@router.post("/submit", response_model=SubmissionRead, status_code=status.HTTP_202_ACCEPTED)
def submit_solution(
    payload: SubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Submission:
    if not db.get(Problem, payload.problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    submission = Submission(
        user_id=current_user.id,
        problem_id=payload.problem_id,
        language=payload.language,
        source_code=payload.source_code,
        status=Verdict.pending,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    if settings.force_inline_judge:
        background_tasks.add_task(_judge_inline, submission.id)
        return submission

    try:
        from app.workers.tasks import judge_submission

        judge_submission.delay(submission.id)
    except Exception:
        background_tasks.add_task(_judge_inline, submission.id)
    return submission


@router.get("/submission/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Submission:
    submission = db.get(Submission, submission_id)
    if not submission or (submission.user_id != current_user.id and not current_user.is_admin):
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/history", response_model=list[SubmissionRead])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Submission]:
    return db.query(Submission).filter(Submission.user_id == current_user.id).order_by(Submission.id.desc()).all()


def _judge_inline(submission_id: int) -> None:
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return
        problem = db.get(Problem, submission.problem_id)
        if not problem:
            return
        result = run_problem_cases(db, problem, submission.source_code, submission.language, hidden=True)
        submission.status = result.status
        submission.execution_time = result.execution_time
        submission.memory = result.memory
        db.commit()
        db.refresh(submission)
        update_leaderboard(db, submission.user)
    finally:
        db.close()
