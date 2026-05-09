from typing import List, Optional, Dict, Generator
from datetime import datetime, timedelta
from src.models.leave import LeaveApplication
from src.models.employee import Employee
from src.storage.json_storage import JSONStorage
from src.storage.logger import logger
from src.config.settings import LEAVE_DATA_FILE, LEAVE_TYPES
from src.services.employee_service import EmployeeService
from src.services.attendance_service import AttendanceService


class LeaveService:
    def __init__(self):
        self.storage = JSONStorage(LEAVE_DATA_FILE)
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.leave_type_rules = {
            "年假": {"description": "带薪年假，需提前申请", "paid": True, "requires_approval": True},
            "病假": {"description": "因病休假，需提供医院证明", "paid": False, "requires_approval": True},
            "事假": {"description": "因私事请假，无薪", "paid": False, "requires_approval": True},
            "婚假": {"description": "结婚休假", "paid": True, "requires_approval": True},
            "产假": {"description": "生育休假", "paid": True, "requires_approval": True},
            "丧假": {"description": "直系亲属丧事休假", "paid": True, "requires_approval": True},
        }

    def get_leave_type_info(self, leave_type: str) -> Dict:
        return self.leave_type_rules.get(
            leave_type, {"description": "其他类型", "paid": False, "requires_approval": True}
        )

    def get_available_leave_types(self) -> List[Dict]:
        return [
            {"type": leave_type, **self.leave_type_rules[leave_type]}
            for leave_type in LEAVE_TYPES
        ]

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

        if leave_type not in LEAVE_TYPES:
            logger.warning(f"请假申请失败：无效的请假类型 {leave_type}")
            return None

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"请假申请失败：日期格式错误")
            return None

        if end_dt < start_dt:
            logger.warning(f"请假申请失败：结束日期早于开始日期")
            return None

        total_days = self._calculate_leave_days(start_dt, end_dt)

        if total_days <= 0:
            logger.warning(f"请假申请失败：无效的请假天数")
            return None

        if self._has_conflict(emp_id, start_date, end_date):
            logger.warning(f"请假申请失败：该时间段已有请假申请")
            return None

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
            logger.info(
                f"请假申请提交成功: {employee.name} - {leave_type} "
                f"({start_date} ~ {end_date}, {total_days}天)"
            )
            return application

        return None

    def approve(
        self, application_id: str, approver: str, remark: str = ""
    ) -> Optional[LeaveApplication]:
        application = self._get_application_by_id(application_id)
        if not application:
            logger.warning(f"审批失败：未找到申请 ID: {application_id}")
            return None

        if application.status != "待审批":
            logger.warning(f"审批失败：申请状态不是待审批: {application.status}")
            return None

        application.status = "已批准"
        application.approver = approver
        application.approval_remark = remark
        application.approved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.storage.update(application_id, application.to_dict()):
            self._update_attendance_for_approved_leave(application)
            logger.info(
                f"请假申请已批准: {application.employee_name} - "
                f"{application.leave_type} - 审批人: {approver}"
            )
            return application

        return None

    def reject(
        self, application_id: str, approver: str, remark: str = ""
    ) -> Optional[LeaveApplication]:
        application = self._get_application_by_id(application_id)
        if not application:
            logger.warning(f"审批失败：未找到申请 ID: {application_id}")
            return None

        if application.status != "待审批":
            logger.warning(f"审批失败：申请状态不是待审批: {application.status}")
            return None

        application.status = "已拒绝"
        application.approver = approver
        application.approval_remark = remark
        application.approved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.storage.update(application_id, application.to_dict()):
            logger.info(
                f"请假申请已拒绝: {application.employee_name} - "
                f"{application.leave_type} - 审批人: {approver}"
            )
            return application

        return None

    def cancel(self, application_id: str) -> bool:
        application = self._get_application_by_id(application_id)
        if not application:
            logger.warning(f"取消失败：未找到申请 ID: {application_id}")
            return False

        if application.status != "待审批":
            logger.warning(f"取消失败：只有待审批状态可以取消: {application.status}")
            return False

        if self.storage.delete(application_id):
            logger.info(f"请假申请已取消: {application.employee_name} - {application.leave_type}")
            return True

        return False

    def get_all_applications(self) -> List[LeaveApplication]:
        data = self.storage.load_all()
        return [LeaveApplication.from_dict(item) for item in data]

    def get_applications_by_employee(self, emp_id: str) -> List[LeaveApplication]:
        records = self.storage.find(employee_id=emp_id)
        applications = [LeaveApplication.from_dict(item) for item in records]
        return sorted(
            applications,
            key=lambda a: a.created_at,
            reverse=True,
        )

    def get_pending_applications(self) -> List[LeaveApplication]:
        records = self.storage.find(status="待审批")
        applications = [LeaveApplication.from_dict(item) for item in records]
        return sorted(
            applications,
            key=lambda a: a.created_at,
        )

    def get_application_by_id(self, application_id: str) -> Optional[LeaveApplication]:
        return self._get_application_by_id(application_id)

    def get_applications_by_type(self, leave_type: str) -> List[LeaveApplication]:
        records = self.storage.find(leave_type=leave_type)
        return [LeaveApplication.from_dict(item) for item in records]

    def get_approved_applications_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[LeaveApplication]:
        applications = self.get_all_applications()
        return [
            app for app in applications
            if app.status == "已批准"
            and not (app.end_date < start_date or app.start_date > end_date)
        ]

    def get_leave_days_by_month(self, emp_id: str, month: str) -> float:
        applications = self.get_applications_by_employee(emp_id)
        total_days = 0.0

        for app in applications:
            if app.status != "已批准":
                continue
            if app.leave_type in ["年假", "婚假", "产假", "丧假"]:
                continue

            try:
                app_start = datetime.strptime(app.start_date, "%Y-%m-%d")
                app_end = datetime.strptime(app.end_date, "%Y-%m-%d")
            except ValueError:
                continue

            month_start = datetime.strptime(f"{month}-01", "%Y-%m-%d")
            next_month = month_start.replace(
                month=month_start.month % 12 + 1,
                year=month_start.year + (1 if month_start.month == 12 else 0),
            )
            month_end = next_month - timedelta(days=1)

            overlap_start = max(app_start, month_start)
            overlap_end = min(app_end, month_end)

            if overlap_start <= overlap_end:
                overlap_days = (overlap_end - overlap_start).days + 1
                total_days += overlap_days

        return total_days

    def count_pending_applications(self) -> int:
        return len(self.get_pending_applications())

    def count_applications_by_status(self, status: str) -> int:
        return len(self.storage.find(status=status))

    def _get_application_by_id(self, application_id: str) -> Optional[LeaveApplication]:
        data = self.storage.get_by_id(application_id)
        return LeaveApplication.from_dict(data) if data else None

    def _calculate_leave_days(self, start_dt: datetime, end_dt: datetime) -> float:
        delta = end_dt - start_dt
        return float(delta.days + 1)

    def _iterate_date_range(self, start_date: str, end_date: str) -> Generator[str, None, None]:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return

        current = start_dt
        while current <= end_dt:
            yield current.strftime("%Y-%m-%d")
            current += timedelta(days=1)

    def _has_conflict(self, emp_id: str, start_date: str, end_date: str) -> bool:
        applications = self.get_applications_by_employee(emp_id)

        for app in applications:
            if app.status in ["已取消"]:
                continue
            if app.end_date < start_date or app.start_date > end_date:
                continue
            if app.status in ["待审批", "已批准"]:
                return True

        return False

    def _update_attendance_for_approved_leave(self, application: LeaveApplication):
        emp_id = application.employee_id
        leave_type = application.leave_type
        remark = application.approval_remark

        for date in self._iterate_date_range(application.start_date, application.end_date):
            self.attendance_service.mark_leave_approved(
                emp_id=emp_id,
                date=date,
                leave_type=leave_type,
                remark=remark,
            )
