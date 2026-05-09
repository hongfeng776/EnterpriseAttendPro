from typing import List, Optional, Dict
from datetime import datetime, timedelta
from src.models.attendance import AttendanceRecord
from src.models.employee import Employee
from src.storage.json_storage import JSONStorage
from src.storage.logger import logger
from src.config.settings import (
    ATTENDANCE_DATA_FILE,
    WORK_START_TIME,
    WORK_END_TIME,
    LATE_THRESHOLD_MINUTES,
)
from src.services.employee_service import EmployeeService


class AttendanceService:
    def __init__(self):
        self.storage = JSONStorage(ATTENDANCE_DATA_FILE)
        self.employee_service = EmployeeService()

    def clock_in(self, emp_id: str) -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"打卡失败：未找到员工 ID: {emp_id}")
            return None

        today = datetime.now().strftime("%Y-%m-%d")
        existing = self._get_record_by_employee_date(emp_id, today)
        if existing and existing.clock_in_time:
            logger.info(f"{employee.name} 今日已上班打卡")
            return existing

        now = datetime.now()
        clock_in_time = now.strftime("%H:%M:%S")
        is_late = self._check_late(now)

        if existing:
            existing.clock_in_time = clock_in_time
            existing.is_late = is_late
            existing.status = self._determine_status(existing)
            if self.storage.update(existing.id, existing.to_dict()):
                logger.info(f"{employee.name} 上班打卡: {clock_in_time} {'(迟到)' if is_late else ''}")
                return existing
        else:
            record = AttendanceRecord(
                id=AttendanceRecord.generate_id(),
                employee_id=emp_id,
                employee_name=employee.name,
                date=today,
                clock_in_time=clock_in_time,
                is_late=is_late,
                status="迟到" if is_late else "正常",
            )
            if self.storage.add(record.to_dict()):
                logger.info(f"{employee.name} 上班打卡: {clock_in_time} {'(迟到)' if is_late else ''}")
                return record

        return None

    def clock_out(self, emp_id: str) -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"打卡失败：未找到员工 ID: {emp_id}")
            return None

        today = datetime.now().strftime("%Y-%m-%d")
        existing = self._get_record_by_employee_date(emp_id, today)
        if not existing or not existing.clock_in_time:
            logger.warning(f"{employee.name} 尚未上班打卡")
            return None

        if existing.clock_out_time:
            logger.info(f"{employee.name} 今日已下班打卡")
            return existing

        now = datetime.now()
        clock_out_time = now.strftime("%H:%M:%S")
        is_early_leave = self._check_early_leave(now)
        overtime_hours = self._calculate_overtime(now)

        existing.clock_out_time = clock_out_time
        existing.is_early_leave = is_early_leave
        existing.overtime_hours = overtime_hours
        existing.status = self._determine_status(existing)

        if self.storage.update(existing.id, existing.to_dict()):
            logger.info(
                f"{employee.name} 下班打卡: {clock_out_time} "
                f"{'(早退)' if is_early_leave else ''} "
                f"(加班 {overtime_hours:.1f}h)"
            )
            return existing

        return None

    def mark_absent(
        self, emp_id: str, date: str, remark: str = ""
    ) -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"标记缺勤失败：未找到员工 ID: {emp_id}")
            return None

        existing = self._get_record_by_employee_date(emp_id, date)
        if existing:
            existing.is_absent = True
            existing.status = "缺勤"
            existing.remark = remark
            if self.storage.update(existing.id, existing.to_dict()):
                logger.info(f"{employee.name} {date} 标记为缺勤")
                return existing
        else:
            record = AttendanceRecord(
                id=AttendanceRecord.generate_id(),
                employee_id=emp_id,
                employee_name=employee.name,
                date=date,
                is_absent=True,
                status="缺勤",
                remark=remark,
            )
            if self.storage.add(record.to_dict()):
                logger.info(f"{employee.name} {date} 标记为缺勤")
                return record

        return None

    def mark_leave_approved(
        self, emp_id: str, date: str, leave_type: str, remark: str = ""
    ) -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"标记请假豁免失败：未找到员工 ID: {emp_id}")
            return None

        existing = self._get_record_by_employee_date(emp_id, date)
        leave_status = f"请假({leave_type})"
        remark_text = f"请假已批准: {leave_type}"
        if remark:
            remark_text = f"{remark_text} - {remark}"

        if existing:
            if existing.status.startswith("请假"):
                return existing

            existing.status = leave_status
            existing.is_absent = False
            existing.remark = remark_text

            if self.storage.update(existing.id, existing.to_dict()):
                logger.info(f"{employee.name} {date} 已豁免为 {leave_type}")
                return existing
        else:
            record = AttendanceRecord(
                id=AttendanceRecord.generate_id(),
                employee_id=emp_id,
                employee_name=employee.name,
                date=date,
                status=leave_status,
                is_absent=False,
                remark=remark_text,
            )
            if self.storage.add(record.to_dict()):
                logger.info(f"{employee.name} {date} 已豁免为 {leave_type}")
                return record

        return None

    def get_records_by_date(self, date: str) -> List[AttendanceRecord]:
        records = self.storage.find(date=date)
        return [AttendanceRecord.from_dict(item) for item in records]

    def get_records_by_month(self, emp_id: str, month: str) -> List[AttendanceRecord]:
        all_records = self.storage.find(employee_id=emp_id)
        month_records = [
            record for record in all_records
            if record.get("date", "").startswith(month)
        ]
        return sorted(
            [AttendanceRecord.from_dict(item) for item in month_records],
            key=lambda r: r.date,
        )

    def get_all_records(self) -> List[AttendanceRecord]:
        data = self.storage.load_all()
        return [AttendanceRecord.from_dict(item) for item in data]

    def calculate_monthly_stats(self, emp_id: str, month: str) -> Dict:
        records = self.get_records_by_month(emp_id, month)

        total_days = len(records)
        normal_days = 0
        late_days = 0
        early_leave_days = 0
        absence_days = 0
        leave_days = 0
        overtime_hours = 0.0

        for record in records:
            if record.status.startswith("请假"):
                leave_days += 1
                continue
            if record.is_absent or record.status == "缺勤":
                absence_days += 1
            else:
                normal_days += 1
            if record.is_late:
                late_days += 1
            if record.is_early_leave:
                early_leave_days += 1
            overtime_hours += record.overtime_hours

        return {
            "total_days": total_days,
            "normal_days": normal_days,
            "late_days": late_days,
            "early_leave_days": early_leave_days,
            "absence_days": absence_days,
            "leave_days": leave_days,
            "overtime_hours": round(overtime_hours, 1),
        }

    def _get_record_by_employee_date(
        self, emp_id: str, date: str
    ) -> Optional[AttendanceRecord]:
        records = self.storage.find(employee_id=emp_id, date=date)
        return AttendanceRecord.from_dict(records[0]) if records else None

    def _check_late(self, now: datetime) -> bool:
        start_time = datetime.combine(now.date(), WORK_START_TIME)
        late_threshold = start_time + timedelta(minutes=LATE_THRESHOLD_MINUTES)
        return now > late_threshold

    def _check_early_leave(self, now: datetime) -> bool:
        end_time = datetime.combine(now.date(), WORK_END_TIME)
        return now < end_time

    def _calculate_overtime(self, now: datetime) -> float:
        end_time = datetime.combine(now.date(), WORK_END_TIME)
        if now > end_time:
            delta = now - end_time
            return round(delta.total_seconds() / 3600, 1)
        return 0.0

    def _determine_status(self, record: AttendanceRecord) -> str:
        if record.status.startswith("请假"):
            return record.status
        if record.is_absent:
            return "缺勤"
        if record.is_late and record.is_early_leave:
            return "迟到+早退"
        if record.is_late:
            return "迟到"
        if record.is_early_leave:
            return "早退"
        return "正常"
