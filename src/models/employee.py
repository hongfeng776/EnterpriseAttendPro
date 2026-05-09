from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Employee:
    id: str
    employee_no: str
    name: str
    gender: str
    department: str
    position: str
    phone: str
    email: str
    join_date: str
    base_salary: float
    status: str = "在职"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "employee_no": self.employee_no,
            "name": self.name,
            "gender": self.gender,
            "department": self.department,
            "position": self.position,
            "phone": self.phone,
            "email": self.email,
            "join_date": self.join_date,
            "base_salary": self.base_salary,
            "status": self.status,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Employee":
        return Employee(
            id=data.get("id", Employee.generate_id()),
            employee_no=data.get("employee_no", ""),
            name=data.get("name", ""),
            gender=data.get("gender", ""),
            department=data.get("department", ""),
            position=data.get("position", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            join_date=data.get("join_date", ""),
            base_salary=float(data.get("base_salary", 0)),
            status=data.get("status", "在职"),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
