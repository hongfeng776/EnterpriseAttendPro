from typing import Dict, List
from collections import defaultdict
from src.services.employee_service import EmployeeService
from src.services.attendance_service import AttendanceService
from src.services.leave_service import LeaveService
from src.services.salary_service import SalaryService
from src.storage.logger import logger
from src.config.settings import DEPARTMENTS


class ReportService:
    def __init__(self):
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.leave_service = LeaveService()
        self.salary_service = SalaryService()

    def generate_employee_report(self) -> Dict:
        employees = self.employee_service.get_all_employees()
        total = len(employees)

        dept_count = defaultdict(int)
        position_count = defaultdict(int)
        status_count = defaultdict(int)
        total_salary = 0.0

        for emp in employees:
            dept_count[emp.department] += 1
            position_count[emp.position] += 1
            status_count[emp.status] += 1
            total_salary += emp.base_salary

        return {
            "report_type": "员工统计报表",
            "total_employees": total,
            "by_department": dict(dept_count),
            "by_position": dict(position_count),
            "by_status": dict(status_count),
            "total_base_salary": round(total_salary, 2),
            "average_base_salary": round(total_salary / total, 2) if total > 0 else 0,
        }

    def generate_attendance_report(self, month: str) -> Dict:
        employees = self.employee_service.get_all_employees()

        total_days = 0
        total_late = 0
        total_early_leave = 0
        total_absence = 0
        total_overtime = 0.0

        dept_stats = defaultdict(lambda: {"employees": 0, "late": 0, "early_leave": 0, "absence": 0})

        for emp in employees:
            stats = self.attendance_service.calculate_monthly_stats(emp.id, month)
            total_days += stats["total_days"]
            total_late += stats["late_days"]
            total_early_leave += stats["early_leave_days"]
            total_absence += stats["absence_days"]
            total_overtime += stats["overtime_hours"]

            dept_stats[emp.department]["employees"] += 1
            dept_stats[emp.department]["late"] += stats["late_days"]
            dept_stats[emp.department]["early_leave"] += stats["early_leave_days"]
            dept_stats[emp.department]["absence"] += stats["absence_days"]

        avg_attendance_rate = (
            (total_days - total_absence) / (total_days if total_days > 0 else 1) * 100
        )

        return {
            "report_type": "考勤统计报表",
            "month": month,
            "total_days_recorded": total_days,
            "total_late_days": total_late,
            "total_early_leave_days": total_early_leave,
            "total_absence_days": total_absence,
            "total_overtime_hours": round(total_overtime, 1),
            "attendance_rate": round(avg_attendance_rate, 2),
            "by_department": {
                dept: {
                    "employee_count": s["employees"],
                    "late_days": s["late"],
                    "early_leave_days": s["early_leave"],
                    "absence_days": s["absence"],
                }
                for dept, s in dept_stats.items()
            },
        }

    def generate_leave_report(self, month: str) -> Dict:
        applications = self.leave_service.get_all_applications()

        month_apps = [
            app for app in applications
            if (app.start_date.startswith(month) or app.end_date.startswith(month))
        ]

        type_count = defaultdict(int)
        type_days = defaultdict(float)
        status_count = defaultdict(int)
        dept_days = defaultdict(float)

        employees = self.employee_service.get_all_employees()
        emp_dept = {emp.id: emp.department for emp in employees}

        for app in month_apps:
            type_count[app.leave_type] += 1
            type_days[app.leave_type] += app.total_days
            status_count[app.status] += 1

            dept = emp_dept.get(app.employee_id, "未分配")
            dept_days[dept] += app.total_days

        return {
            "report_type": "请假统计报表",
            "month": month,
            "total_applications": len(month_apps),
            "by_type": {
                leave_type: {
                    "count": type_count.get(leave_type, 0),
                    "total_days": round(type_days.get(leave_type, 0), 1),
                }
                for leave_type in set(type_count.keys())
            },
            "by_status": dict(status_count),
            "by_department": {
                dept: {"total_days": round(days, 1)}
                for dept, days in dept_days.items()
            },
        }

    def generate_salary_report(self, month: str) -> Dict:
        summary = self.salary_service.get_monthly_summary(month)
        records = self.salary_service.get_records_by_month(month)

        dept_salary = defaultdict(lambda: {"count": 0, "total": 0.0, "avg": 0.0})

        for record in records:
            dept_salary[record.department]["count"] += 1
            dept_salary[record.department]["total"] += record.net_salary

        for dept in dept_salary:
            if dept_salary[dept]["count"] > 0:
                dept_salary[dept]["avg"] = round(
                    dept_salary[dept]["total"] / dept_salary[dept]["count"], 2
                )
            dept_salary[dept]["total"] = round(dept_salary[dept]["total"], 2)

        return {
            "report_type": "薪资统计报表",
            "month": month,
            "summary": summary,
            "by_department": {
                dept: {
                    "employee_count": s["count"],
                    "total_salary": s["total"],
                    "average_salary": s["avg"],
                }
                for dept, s in dept_salary.items()
            },
        }

    def generate_employee_attendance_report(self, emp_id: str, month: str) -> Dict:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            return {"error": "员工不存在"}

        attendance_stats = self.attendance_service.calculate_monthly_stats(emp_id, month)
        records = self.attendance_service.get_records_by_month(emp_id, month)

        leave_days = self.leave_service.get_leave_days_by_month(emp_id, month)

        return {
            "report_type": "员工个人考勤报表",
            "month": month,
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "department": employee.department,
                "position": employee.position,
            },
            "attendance_stats": attendance_stats,
            "leave_days": leave_days,
            "records": [
                {
                    "date": r.date,
                    "clock_in": r.clock_in_time,
                    "clock_out": r.clock_out_time,
                    "status": r.status,
                    "is_late": r.is_late,
                    "is_early_leave": r.is_early_leave,
                    "overtime_hours": r.overtime_hours,
                }
                for r in records
            ],
        }

    def generate_employee_salary_report(self, emp_id: str, month: str) -> Dict:
        employee = self.employee_service.get_employee_by_id(emp_id)
        if not employee:
            return {"error": "员工不存在"}

        salary_record = self.salary_service.get_record_by_employee_month(emp_id, month)
        if not salary_record:
            return {"error": "暂无该月薪资数据"}

        return {
            "report_type": "员工个人薪资报表",
            "month": month,
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "department": employee.department,
                "position": employee.position,
            },
            "salary_details": {
                "base_salary": salary_record.base_salary,
                "overtime_pay": salary_record.overtime_pay,
                "bonus": salary_record.bonus,
                "late_deduction": salary_record.late_deduction,
                "early_leave_deduction": salary_record.early_leave_deduction,
                "absence_deduction": salary_record.absence_deduction,
                "leave_deduction": salary_record.leave_deduction,
                "net_salary": salary_record.net_salary,
            },
            "status": salary_record.status,
            "paid_at": salary_record.paid_at,
        }

    def generate_dashboard_report(self) -> Dict:
        today = __import__("datetime").datetime.now()
        current_month = today.strftime("%Y-%m")

        employee_report = self.generate_employee_report()
        attendance_report = self.generate_attendance_report(current_month)
        leave_report = self.generate_leave_report(current_month)
        salary_report = self.generate_salary_report(current_month)

        pending_leave = self.leave_service.count_pending_applications()
        today_attendance = self.attendance_service.get_records_by_date(today.strftime("%Y-%m-%d"))

        return {
            "report_type": "仪表盘概览",
            "current_month": current_month,
            "today": today.strftime("%Y-%m-%d"),
            "employee_summary": {
                "total": employee_report["total_employees"],
                "active": employee_report["by_status"].get("在职", 0),
            },
            "attendance_today": {
                "total_punched": len(today_attendance),
                "late": sum(1 for r in today_attendance if r.is_late),
            },
            "attendance_monthly": {
                "attendance_rate": attendance_report["attendance_rate"],
                "late_days": attendance_report["total_late_days"],
                "overtime_hours": attendance_report["total_overtime_hours"],
            },
            "leave_summary": {
                "pending_approval": pending_leave,
                "total_month_applications": leave_report["total_applications"],
            },
            "salary_summary": salary_report["summary"],
        }
