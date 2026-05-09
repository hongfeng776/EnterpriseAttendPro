from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class AttendanceRecord:
    id: str
    employee_id: str
    employee_name: str
    date: str
    clock_in_time: Optional[str] = None
    clock_out_time: Optional[str] = None
    status: str = "正常"
    is_late: bool = False
    is_early_leave: bool = False
    is_absent: bool = False
    overtime_hours: float = 0.0
    remark: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "date": self.date,
            "clock_in_time": self.clock_in_time,
            "clock_out_time": self.clock_out_time,
            "status": self.status,
            "is_late": self.is_late,
            "is_early_leave": self.is_early_leave,
            "is_absent": self.is_absent,
            "overtime_hours": self.overtime_hours,
            "remark": self.remark,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "AttendanceRecord":
        return AttendanceRecord(
            id=data.get("id", AttendanceRecord.generate_id()),
            employee_id=data.get("employee_id", ""),
            employee_name=data.get("employee_name", ""),
            date=data.get("date", ""),
            clock_in_time=data.get("clock_in_time"),
            clock_out_time=data.get("clock_out_time"),
            status=data.get("status", "正常"),
            is_late=data.get("is_late", False),
            is_early_leave=data.get("is_early_leave", False),
            is_absent=data.get("is_absent", False),
            overtime_hours=float(data.get("overtime_hours", 0.0)),
            remark=data.get("remark", ""),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
