from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import require_admin
from app.config.database import get_db
from app.models.entities import Problem, Submission, TestCase, User

router = APIRouter(tags=["Admin"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict[str, int]:
    return {
        "users": db.query(User).count(),
        "problems": db.query(Problem).count(),
        "test_cases": db.query(TestCase).count(),
        "submissions": db.query(Submission).count(),
        "banned_users": db.query(User).filter(User.is_banned.is_(True)).count(),
    }


@router.get("/admin/submissions")
def submissions(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[dict]:
    rows = db.query(Submission).order_by(Submission.id.desc()).limit(200).all()
    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "problem_id": row.problem_id,
            "language": row.language,
            "status": row.status.value,
            "execution_time": row.execution_time,
            "memory": row.memory,
        }
        for row in rows
    ]


@router.post("/admin/users/{user_id}/ban")
def ban_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict[str, str]:
    user = db.get(User, user_id)
    if user:
        user.is_banned = True
        db.commit()
    return {"message": "User banned"}
