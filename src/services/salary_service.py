from typing import List, Optional, Dict
from datetime import datetime
from src.models.salary import SalaryRecord
from src.models.employee import Employee
from src.storage.json_storage import JSONStorage
from src.storage.logger import logger
from src.config.settings import (
    SALARY_DATA_FILE,
    OVERTIME_RATE,
    LATE_DEDUCTION,
    EARLY_LEAVE_DEDUCTION,
    ABSENCE_DEDUCTION,
)
from src.services.employee_service import EmployeeService
from src.services.attendance_service import AttendanceService
from src.services.leave_service import LeaveService


class SalaryService:
    def __init__(self):
        self.storage = JSONStorage(SALARY_DATA_FILE)
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.leave_service = LeaveService()

    def _calculate_daily_salary(self, base_salary: float, work_days: int = 22) -> float:
        return base_salary / work_days if work_days > 0 else 0

    def calculate_salary(
        self,
        employee: Employee,
        month: str,
        bonus: float = 0,
        custom_deductions: Dict[str, float] = None,
    ) -> Optional[SalaryRecord]:
        if custom_deductions is None:
            custom_deductions = {}

        attendance_stats = self.attendance_service.calculate_monthly_stats(
            employee.id, month
        )

        daily_salary = self._calculate_daily_salary(employee.base_salary)

        overtime_pay = round(attendance_stats["overtime_hours"] * daily_salary * OVERTIME_RATE / 8, 2)
        late_deduction = round(attendance_stats["late_days"] * LATE_DEDUCTION, 2)
        early_leave_deduction = round(attendance_stats["early_leave_days"] * EARLY_LEAVE_DEDUCTION, 2)
        absence_deduction = round(attendance_stats["absence_days"] * ABSENCE_DEDUCTION, 2)

        leave_days = self.leave_service.get_leave_days_by_month(employee.id, month)
        leave_deduction = round(leave_days * daily_salary, 2)

        net_salary = round(
            employee.base_salary
            + overtime_pay
            + bonus
            - late_deduction
            - early_leave_deduction
            - absence_deduction
            - leave_deduction,
            2,
        )

        for ded_name, ded_amount in custom_deductions.items():
            net_salary -= ded_amount

        net_salary = max(0, net_salary)

        return SalaryRecord(
            id=SalaryRecord.generate_id(),
            employee_id=employee.id,
            employee_name=employee.name,
            department=employee.department,
            month=month,
            base_salary=employee.base_salary,
            overtime_pay=overtime_pay,
            late_deduction=late_deduction,
            early_leave_deduction=early_leave_deduction,
            absence_deduction=absence_deduction,
            leave_deduction=leave_deduction,
            bonus=bonus,
            net_salary=net_salary,
        )

    def generate_monthly_salary(self, month: str, bonuses: Dict[str, float] = None) -> List[SalaryRecord]:
        if bonuses is None:
            bonuses = {}

        employees = self.employee_service.get_all_employees()
        salary_records = []

        existing_records = self.get_records_by_month(month)
        existing_ids = {r.employee_id for r in existing_records}

        for employee in employees:
            if employee.id in existing_ids:
                continue

            if employee.status != "在职":
                continue

            bonus = bonuses.get(employee.id, 0)
            salary_record = self.calculate_salary(employee, month, bonus)

            if salary_record and self.storage.add(salary_record.to_dict()):
                salary_records.append(salary_record)
                logger.info(f"生成薪资: {employee.name} - {month} - {salary_record.net_salary}元")

        return salary_records

    def calculate_single_salary(
        self,
        emp_id: str,
        month: str,
        bonus: float = 0,
        force_recalculate: bool = False,
    ) -> Optional[SalaryRecord]:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"薪资计算失败：未找到员工 ID: {emp_id}")
            return None

        existing = self.get_record_by_employee_month(emp_id, month)
        if existing and not force_recalculate:
            logger.info(f"薪资已存在: {employee.name} - {month}")
            return existing

        salary_record = self.calculate_salary(employee, month, bonus)
        if not salary_record:
            return None

        if existing:
            salary_record.id = existing.id
            salary_record.status = existing.status
            salary_record.paid_at = existing.paid_at
            if self.storage.update(existing.id, salary_record.to_dict()):
                logger.info(f"更新薪资: {employee.name} - {month}")
                return salary_record
        else:
            if self.storage.add(salary_record.to_dict()):
                logger.info(f"生成薪资: {employee.name} - {month}")
                return salary_record

        return None

    def get_all_records(self) -> List[SalaryRecord]:
        data = self.storage.load_all()
        return [SalaryRecord.from_dict(item) for item in data]

    def get_records_by_month(self, month: str) -> List[SalaryRecord]:
        records = self.storage.find(month=month)
        return [SalaryRecord.from_dict(item) for item in records]

    def get_records_by_employee(self, emp_id: str) -> List[SalaryRecord]:
        records = self.storage.find(employee_id=emp_id)
        return [SalaryRecord.from_dict(item) for item in records]

    def get_record_by_employee_month(self, emp_id: str, month: str) -> Optional[SalaryRecord]:
        records = self.get_records_by_month(month)
        for record in records:
            if record.employee_id == emp_id:
                return record
        return None

    def get_record_by_id(self, record_id: str) -> Optional[SalaryRecord]:
        data = self.storage.get_by_id(record_id)
        return SalaryRecord.from_dict(data) if data else None

    def pay_salary(self, record_id: str, remark: str = "") -> Optional[SalaryRecord]:
        record = self.get_record_by_id(record_id)
        if not record:
            logger.warning(f"发薪失败：未找到薪资记录 ID: {record_id}")
            return None

        if record.status == "已发放":
            logger.warning(f"发薪失败：该薪资已发放")
            return None

        record.status = "已发放"
        record.paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record.remark = remark

        if self.storage.update(record_id, record.to_dict()):
            logger.info(f"薪资发放: {record.employee_name} - {record.month} - {record.net_salary}元")
            return record
        return None

    def batch_pay_salary(self, month: str) -> List[SalaryRecord]:
        records = self.get_records_by_month(month)
        paid_records = []

        for record in records:
            if record.status == "未发放":
                paid_record = self.pay_salary(record.id, f"批量发放 - {month}")
                if paid_record:
                    paid_records.append(paid_record)

        return paid_records

    def get_monthly_summary(self, month: str) -> Dict:
        records = self.get_records_by_month(month)
        total_employees = len(records)
        total_base_salary = sum(r.base_salary for r in records)
        total_overtime_pay = sum(r.overtime_pay for r in records)
        total_bonus = sum(r.bonus for r in records)
        total_deductions = sum(
            r.late_deduction
            + r.early_leave_deduction
            + r.absence_deduction
            + r.leave_deduction
            for r in records
        )
        total_net_salary = sum(r.net_salary for r in records)
        paid_records = [r for r in records if r.status == "已发放"]

        return {
            "month": month,
            "total_employees": total_employees,
            "total_base_salary": round(total_base_salary, 2),
            "total_overtime_pay": round(total_overtime_pay, 2),
            "total_bonus": round(total_bonus, 2),
            "total_deductions": round(total_deductions, 2),
            "total_net_salary": round(total_net_salary, 2),
            "paid_count": len(paid_records),
            "unpaid_count": total_employees - len(paid_records),
            "average_salary": round(total_net_salary / total_employees, 2) if total_employees > 0 else 0,
        }
