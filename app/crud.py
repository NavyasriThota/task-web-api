from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import Student


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    return db.query(Student).filter(Student.email.ilike(email)).first()


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    return db.query(Student).filter(Student.student_id == student_id).first()


def get_students(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Student).order_by(Student.student_id.asc()).offset(skip).limit(limit).all()


def get_total_count(db: Session) -> int:
    return db.query(Student).count()


def search_students(db: Session, name: str):
    search_term = name.strip()
    if len(search_term) < 3:
        raise ValueError("Search term must contain at least 3 characters.")

    query = db.query(Student).filter(
        or_(
            Student.first_name.ilike(f"%{search_term}%"),
            Student.last_name.ilike(f"%{search_term}%"),
            (Student.first_name + " " + Student.last_name).ilike(f"%{search_term}%"),
            Student.email.ilike(f"%{search_term}%"),
        )
    )
    return query.order_by(Student.student_id.asc()).all()


def create_student(db: Session, student_data):
    email = student_data.email.lower()
    existing = get_student_by_email(db, email)
    if existing:
        raise ValueError("A student with this email already exists.")

    student = Student(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        email=email,
        phone_number=student_data.phone_number,
        gender=student_data.gender,
        date_of_birth=student_data.date_of_birth,
        course=student_data.course,
        batch=student_data.batch,
        address=student_data.address,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student_id: int, update_data):
    student = get_student_by_id(db, student_id)
    if not student:
        raise LookupError("Student not found.")

    new_data = update_data.model_dump(exclude_unset=True, exclude_none=True)
    if "email" in new_data:
        new_email = str(new_data["email"]).lower()
        if new_email != student.email.lower():
            duplicate = get_student_by_email(db, new_email)
            if duplicate:
                raise ValueError("A student with this email already exists.")

    for field, value in new_data.items():
        setattr(student, field, value)

    student.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int) -> bool:
    student = get_student_by_id(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True
