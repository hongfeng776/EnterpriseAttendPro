from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class SalaryRecord:
    id: str
    employee_id: str
    employee_name: str
    department: str
    month: str
    base_salary: float
    overtime_pay: float
    late_deduction: float
    early_leave_deduction: float
    absence_deduction: float
    leave_deduction: float
    bonus: float
    net_salary: float
    status: str = "未发放"
    remark: str = ""
    paid_at: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "department": self.department,
            "month": self.month,
            "base_salary": self.base_salary,
            "overtime_pay": self.overtime_pay,
            "late_deduction": self.late_deduction,
            "early_leave_deduction": self.early_leave_deduction,
            "absence_deduction": self.absence_deduction,
            "leave_deduction": self.leave_deduction,
            "bonus": self.bonus,
            "net_salary": self.net_salary,
            "status": self.status,
            "remark": self.remark,
            "paid_at": self.paid_at,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "SalaryRecord":
        return SalaryRecord(
            id=data.get("id", SalaryRecord.generate_id()),
            employee_id=data.get("employee_id", ""),
            employee_name=data.get("employee_name", ""),
            department=data.get("department", ""),
            month=data.get("month", ""),
            base_salary=float(data.get("base_salary", 0)),
            overtime_pay=float(data.get("overtime_pay", 0)),
            late_deduction=float(data.get("late_deduction", 0)),
            early_leave_deduction=float(data.get("early_leave_deduction", 0)),
            absence_deduction=float(data.get("absence_deduction", 0)),
            leave_deduction=float(data.get("leave_deduction", 0)),
            bonus=float(data.get("bonus", 0)),
            net_salary=float(data.get("net_salary", 0)),
            status=data.get("status", "未发放"),
            remark=data.get("remark", ""),
            paid_at=data.get("paid_at", ""),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
