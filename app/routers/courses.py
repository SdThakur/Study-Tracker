from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from app.models import Course, CourseCreate, CoursePublic, CourseUpdate
from app.security import CurrentUser, SessionDep

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CoursePublic, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    course = Course.model_validate(course_in, update={"user_id": current_user.id})
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.get("/", response_model=list[CoursePublic])
def list_courses(
    current_user: CurrentUser,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    stmt = (
        select(Course)
        .where(Course.user_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(stmt).all()


@router.get("/{course_id}", response_model=CoursePublic)
def get_course(
    course_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return course


@router.patch("/{course_id}", response_model=CoursePublic)
def update_course(
    course_id: int,
    data: CourseUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    update_dict = data.model_dump(exclude_unset=True)
    course.sqlmodel_update(update_dict)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    session.delete(course)
    session.commit()
