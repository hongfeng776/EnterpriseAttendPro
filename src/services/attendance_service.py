from typing import List, Optional
from datetime import datetime, time
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

    def _get_today_date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _get_current_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _parse_time(self, time_str: str) -> time:
        return datetime.strptime(time_str, "%H:%M:%S").time()

    def _is_late(self, clock_in_time: str) -> bool:
        in_time = self._parse_time(clock_in_time)
        if in_time > WORK_START_TIME:
            return True
        return False

    def _is_early_leave(self, clock_out_time: str) -> bool:
        out_time = self._parse_time(clock_out_time)
        if out_time < WORK_END_TIME:
            return True
        return False

    def _calculate_overtime(self, clock_out_time: str) -> float:
        out_time = self._parse_time(clock_out_time)
        end_hours = WORK_END_TIME.hour + WORK_END_TIME.minute / 60
        out_hours = out_time.hour + out_time.minute / 60
        if out_hours > end_hours:
            return round(out_hours - end_hours, 1)
        return 0.0

    def clock_in(self, emp_id: str) -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"打卡失败：未找到员工 ID: {emp_id}")
            return None

        today = self._get_today_date()
        existing_record = self.get_record_by_date(emp_id, today)

        if existing_record:
            if existing_record.clock_in_time:
                logger.warning(f"打卡失败：{employee.name} 今日已打卡")
                return None

            existing_record.clock_in_time = self._get_current_time()
            existing_record.is_late = self._is_late(existing_record.clock_in_time)
            existing_record.status = "已打卡" if not existing_record.is_late else "迟到"

            if self.storage.update(existing_record.id, existing_record.to_dict()):
                logger.info(f"上班打卡: {employee.name} - {existing_record.clock_in_time}")
                return existing_record
            return None

        current_time = self._get_current_time()
        is_late = self._is_late(current_time)
        record = AttendanceRecord(
            id=AttendanceRecord.generate_id(),
            employee_id=emp_id,
            employee_name=employee.name,
            date=today,
            clock_in_time=current_time,
            status="已打卡" if not is_late else "迟到",
            is_late=is_late,
        )

        if self.storage.add(record.to_dict()):
            logger.info(f"上班打卡: {employee.name} - {current_time}")
            return record
        return None

    def clock_out(self, emp_id: str) -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"打卡失败：未找到员工 ID: {emp_id}")
            return None

        today = self._get_today_date()
        record = self.get_record_by_date(emp_id, today)

        if not record:
            logger.warning(f"打卡失败：{employee.name} 今日未上班打卡")
            return None

        if record.clock_out_time:
            logger.warning(f"打卡失败：{employee.name} 今日已下班打卡")
            return None

        current_time = self._get_current_time()
        record.clock_out_time = current_time
        record.is_early_leave = self._is_early_leave(current_time)
        record.overtime_hours = self._calculate_overtime(current_time)

        if record.is_late and record.is_early_leave:
            record.status = "迟到早退"
        elif record.is_late:
            record.status = "迟到"
        elif record.is_early_leave:
            record.status = "早退"
        else:
            record.status = "正常"

        if self.storage.update(record.id, record.to_dict()):
            logger.info(f"下班打卡: {employee.name} - {current_time}")
            return record
        return None

    def get_record_by_date(self, emp_id: str, date: str) -> Optional[AttendanceRecord]:
        records = self.storage.find(employee_id=emp_id, date=date)
        return AttendanceRecord.from_dict(records[0]) if records else None

    def get_all_records(self) -> List[AttendanceRecord]:
        data = self.storage.load_all()
        return [AttendanceRecord.from_dict(item) for item in data]

    def get_records_by_employee(self, emp_id: str) -> List[AttendanceRecord]:
        records = self.storage.find(employee_id=emp_id)
        return [AttendanceRecord.from_dict(item) for item in records]

    def get_records_by_date(self, date: str) -> List[AttendanceRecord]:
        records = self.storage.find(date=date)
        return [AttendanceRecord.from_dict(item) for item in records]

    def get_records_by_month(self, emp_id: str, month: str) -> List[AttendanceRecord]:
        all_records = self.get_records_by_employee(emp_id)
        return [r for r in all_records if r.date.startswith(month)]

    def calculate_monthly_stats(self, emp_id: str, month: str) -> dict:
        records = self.get_records_by_month(emp_id, month)
        stats = {
            "total_days": len(records),
            "late_days": 0,
            "early_leave_days": 0,
            "absence_days": 0,
            "overtime_hours": 0.0,
            "normal_days": 0,
        }

        for record in records:
            if record.is_late:
                stats["late_days"] += 1
            if record.is_early_leave:
                stats["early_leave_days"] += 1
            if record.is_absent:
                stats["absence_days"] += 1
            if record.status == "正常":
                stats["normal_days"] += 1
            stats["overtime_hours"] += record.overtime_hours

        return stats

    def mark_absent(self, emp_id: str, date: str, remark: str = "") -> Optional[AttendanceRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            return None

        existing = self.get_record_by_date(emp_id, date)
        if existing:
            existing.is_absent = True
            existing.status = "缺勤"
            existing.remark = remark
            if self.storage.update(existing.id, existing.to_dict()):
                logger.info(f"标记缺勤: {employee.name} - {date}")
                return existing
            return None

        record = AttendanceRecord(
            id=AttendanceRecord.generate_id(),
            employee_id=emp_id,
            employee_name=employee.name,
            date=date,
            status="缺勤",
            is_absent=True,
            remark=remark,
        )

        if self.storage.add(record.to_dict()):
            logger.info(f"标记缺勤: {employee.name} - {date}")
            return record
        return None
