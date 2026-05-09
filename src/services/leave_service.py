from typing import List, Optional
from datetime import datetime
from src.models.leave import LeaveApplication
from src.storage.json_storage import JSONStorage
from src.storage.logger import logger
from src.config.settings import LEAVE_DATA_FILE, LEAVE_STATUS
from src.services.employee_service import EmployeeService


class LeaveService:
    def __init__(self):
        self.storage = JSONStorage(LEAVE_DATA_FILE)
        self.employee_service = EmployeeService()

    def _calculate_days(self, start_date: str, end_date: str) -> float:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days + 1
            return max(1.0, float(days))
        except ValueError:
            return 1.0

    def apply_leave(
        self,
        emp_id: str,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: str,
    ) -> Optional[LeaveApplication]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"请假申请失败：未找到员工 ID: {emp_id}")
            return None

        total_days = self._calculate_days(start_date, end_date)

        application = LeaveApplication(
            id=LeaveApplication.generate_id(),
            employee_id=emp_id,
            employee_name=employee.name,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=reason,
            status="待审批",
        )

        if self.storage.add(application.to_dict()):
            logger.info(f"请假申请提交: {employee.name} - {leave_type} ({start_date} ~ {end_date})")
            return application
        return None

    def get_all_applications(self) -> List[LeaveApplication]:
        data = self.storage.load_all()
        return [LeaveApplication.from_dict(item) for item in data]

    def get_application_by_id(self, app_id: str) -> Optional[LeaveApplication]:
        data = self.storage.get_by_id(app_id)
        return LeaveApplication.from_dict(data) if data else None

    def get_applications_by_employee(self, emp_id: str) -> List[LeaveApplication]:
        applications = self.storage.find(employee_id=emp_id)
        return [LeaveApplication.from_dict(item) for item in applications]

    def get_applications_by_status(self, status: str) -> List[LeaveApplication]:
        applications = self.storage.find(status=status)
        return [LeaveApplication.from_dict(item) for item in applications]

    def get_pending_applications(self) -> List[LeaveApplication]:
        return self.get_applications_by_status("待审批")

    def approve(
        self,
        app_id: str,
        approver: str,
        approval_remark: str = "",
    ) -> Optional[LeaveApplication]:
        application = self.get_application_by_id(app_id)
        if not application:
            logger.warning(f"审批失败：未找到申请 ID: {app_id}")
            return None

        if application.status != "待审批":
            logger.warning(f"审批失败：该申请已{application.status}")
            return None

        application.status = "已批准"
        application.approver = approver
        application.approval_remark = approval_remark
        application.approved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.storage.update(app_id, application.to_dict()):
            logger.info(f"请假批准: {application.employee_name} - {application.leave_type}")
            return application
        return None

    def reject(
        self,
        app_id: str,
        approver: str,
        approval_remark: str = "",
    ) -> Optional[LeaveApplication]:
        application = self.get_application_by_id(app_id)
        if not application:
            logger.warning(f"审批失败：未找到申请 ID: {app_id}")
            return None

        if application.status != "待审批":
            logger.warning(f"审批失败：该申请已{application.status}")
            return None

        application.status = "已拒绝"
        application.approver = approver
        application.approval_remark = approval_remark
        application.approved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.storage.update(app_id, application.to_dict()):
            logger.info(f"请假拒绝: {application.employee_name} - {application.leave_type}")
            return application
        return None

    def cancel(self, app_id: str) -> bool:
        application = self.get_application_by_id(app_id)
        if not application:
            return False

        if application.status != "待审批":
            logger.warning(f"取消失败：该申请已{application.status}")
            return False

        result = self.storage.delete(app_id)
        if result:
            logger.info(f"请假申请取消: {application.employee_name}")
        return result

    def get_leave_days_by_month(self, emp_id: str, month: str) -> float:
        applications = self.get_applications_by_employee(emp_id)
        total_days = 0.0

        for app in applications:
            if app.status == "已批准" and (
                app.start_date.startswith(month) or app.end_date.startswith(month)
            ):
                total_days += app.total_days

        return total_days

    def count_pending_applications(self) -> int:
        return len(self.get_pending_applications())
