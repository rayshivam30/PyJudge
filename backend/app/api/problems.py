from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import require_admin
from app.config.database import get_db
from app.models.entities import Problem, TestCase, User
from app.schemas.problem import ProblemCreate, ProblemDetail, ProblemRead, ProblemUpdate, TestCaseCreate, TestCaseRead

router = APIRouter(tags=["Problems"])


@router.get("/problems", response_model=list[ProblemRead])
def list_problems(db: Session = Depends(get_db)) -> list[Problem]:
    return db.query(Problem).order_by(Problem.id.desc()).all()


@router.get("/problem/{problem_id}", response_model=ProblemDetail)
def get_problem(problem_id: int, db: Session = Depends(get_db)) -> Problem:
    problem = db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem.test_cases = [case for case in problem.test_cases if not case.is_hidden]
    return problem


@router.get("/problem/{problem_id}/samples", response_model=list[TestCaseRead])
def get_samples(problem_id: int, db: Session = Depends(get_db)) -> list[TestCase]:
    return db.query(TestCase).filter(TestCase.problem_id == problem_id, TestCase.is_hidden.is_(False)).all()


@router.post("/problem", response_model=ProblemDetail, status_code=status.HTTP_201_CREATED)
def create_problem(payload: ProblemCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Problem:
    test_cases = payload.test_cases
    problem_data = payload.model_dump(exclude={"test_cases"})
    problem = Problem(**problem_data)
    problem.test_cases = [TestCase(**case.model_dump()) for case in test_cases]
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@router.put("/problem/{problem_id}", response_model=ProblemRead)
def update_problem(
    problem_id: int,
    payload: ProblemUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Problem:
    problem = db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(problem, key, value)
    db.commit()
    db.refresh(problem)
    return problem


@router.delete("/problem/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_problem(problem_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> None:
    problem = db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    db.delete(problem)
    db.commit()


@router.post("/testcases", response_model=TestCaseRead, status_code=status.HTTP_201_CREATED)
def add_test_case(payload: TestCaseCreate, problem_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> TestCase:
    if not db.get(Problem, problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    test_case = TestCase(problem_id=problem_id, **payload.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case
