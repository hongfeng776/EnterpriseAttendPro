from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class LeaveApplication:
    id: str
    employee_id: str
    employee_name: str
    leave_type: str
    start_date: str
    end_date: str
    total_days: float
    reason: str
    status: str = "待审批"
    approver: str = ""
    approval_remark: str = ""
    approved_at: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "leave_type": self.leave_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_days": self.total_days,
            "reason": self.reason,
            "status": self.status,
            "approver": self.approver,
            "approval_remark": self.approval_remark,
            "approved_at": self.approved_at,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "LeaveApplication":
        return LeaveApplication(
            id=data.get("id", LeaveApplication.generate_id()),
            employee_id=data.get("employee_id", ""),
            employee_name=data.get("employee_name", ""),
            leave_type=data.get("leave_type", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            total_days=float(data.get("total_days", 0)),
            reason=data.get("reason", ""),
            status=data.get("status", "待审批"),
            approver=data.get("approver", ""),
            approval_remark=data.get("approval_remark", ""),
            approved_at=data.get("approved_at", ""),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
