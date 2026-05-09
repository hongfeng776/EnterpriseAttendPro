import os
import sys
from datetime import datetime
from typing import Optional

from src.services.employee_service import EmployeeService
from src.services.attendance_service import AttendanceService
from src.services.leave_service import LeaveService
from src.services.salary_service import SalaryService
from src.services.report_service import ReportService
from src.services.config_service import SystemConfigService
from src.storage.logger import logger


class Menu:
    def __init__(self):
        self.employee_service = EmployeeService()
        self.attendance_service = AttendanceService()
        self.leave_service = LeaveService()
        self.salary_service = SalaryService()
        self.report_service = ReportService()
        self.config_service = SystemConfigService()

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def wait_enter(self):
        input("\n按回车键继续...")

    def print_header(self, title: str):
        self.clear_screen()
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_menu(self, options: dict):
        for key, value in options.items():
            print(f"  {key}. {value}")
        print("-" * 60)

    def input_str(self, prompt: str, default: str = "", allow_empty: bool = False) -> str:
        while True:
            value = input(f"{prompt}").strip()
            if value:
                return value
            if allow_empty:
                return default
            print("  输入不能为空，请重新输入！")

    def input_int(self, prompt: str, default: int = None) -> int:
        while True:
            value = input(f"{prompt}").strip()
            if not value and default is not None:
                return default
            try:
                return int(value)
            except ValueError:
                print("  请输入有效数字！")

    def input_float(self, prompt: str, default: float = None) -> float:
        while True:
            value = input(f"{prompt}").strip()
            if not value and default is not None:
                return default
            try:
                return float(value)
            except ValueError:
                print("  请输入有效数字！")

    def input_date(self, prompt: str, allow_empty: bool = False) -> str:
        while True:
            value = input(f"{prompt}").strip()
            if not value:
                if allow_empty:
                    return ""
                print("  日期不能为空！")
                continue
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("  日期格式错误，请使用 YYYY-MM-DD 格式！")

    def input_month(self, prompt: str, allow_empty: bool = False) -> str:
        while True:
            value = input(f"{prompt}").strip()
            if not value:
                if allow_empty:
                    return ""
                print("  月份不能为空！")
                continue
            try:
                datetime.strptime(value, "%Y-%m")
                return value
            except ValueError:
                print("  月份格式错误，请使用 YYYY-MM 格式！")


class AttendanceSystem(Menu):
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        logger.info("系统启动")
        while self.running:
            self.show_main_menu()
        logger.info("系统退出")
        print("\n感谢使用企业级员工考勤管理系统，再见！\n")

    def show_main_menu(self):
        self.print_header("企业级员工考勤管理系统")
        dashboard = self.report_service.generate_dashboard_report()

        print(f"\n  今日日期: {dashboard['today']}")
        print(f"  当前月份: {dashboard['current_month']}")
        print(f"\n  【概览】")
        print(f"    员工总数: {dashboard['employee_summary']['total']} 人")
        print(f"    在职员工: {dashboard['employee_summary']['active']} 人")
        print(f"    今日打卡: {dashboard['attendance_today']['total_punched']} 人")
        print(f"    待审批请假: {dashboard['leave_summary']['pending_approval']} 条")
        print(f"    本月出勤率: {dashboard['attendance_monthly']['attendance_rate']}%")

        self.print_menu({
            "1": "员工管理",
            "2": "考勤打卡",
            "3": "请假审批",
            "4": "薪资核算",
            "5": "数据报表",
            "6": "系统配置",
            "0": "退出系统",
        })

        choice = self.input_int("请选择操作 [0-6]: ")
        self.handle_main_choice(choice)

    def handle_main_choice(self, choice: int):
        if choice == 1:
            self.employee_management_menu()
        elif choice == 2:
            self.attendance_menu()
        elif choice == 3:
            self.leave_menu()
        elif choice == 4:
            self.salary_menu()
        elif choice == 5:
            self.report_menu()
        elif choice == 6:
            self.config_menu()
        elif choice == 0:
            self.running = False
        else:
            print("  无效的选择！")
            self.wait_enter()

    def employee_management_menu(self):
        while True:
            self.print_header("员工管理")
            self.print_menu({
                "1": "添加员工",
                "2": "查看所有员工",
                "3": "搜索员工",
                "4": "更新员工信息",
                "5": "删除员工",
                "6": "按部门查看",
                "7": "多条件筛选",
                "8": "批量导入员工",
                "9": "导出员工报表",
                "0": "返回主菜单",
            })

            choice = self.input_int("请选择操作 [0-9]: ")

            if choice == 0:
                break
            elif choice == 1:
                self.add_employee()
            elif choice == 2:
                self.list_employees()
            elif choice == 3:
                self.search_employees()
            elif choice == 4:
                self.update_employee()
            elif choice == 5:
                self.delete_employee()
            elif choice == 6:
                self.list_by_department()
            elif choice == 7:
                self.filter_employees_ui()
            elif choice == 8:
                self.batch_import_employees()
            elif choice == 9:
                self.export_employees_report()
            else:
                print("  无效的选择！")
            self.wait_enter()

    def add_employee(self):
        self.print_header("添加员工")
        print("\n请输入员工信息（留空使用默认值）\n")

        name = self.input_str("姓名: ")
        gender = self.input_str("性别 (男/女): ")
        department = self.input_str(f"部门: ")
        position = self.input_str("职位: ")
        phone = self.input_str("电话: ")
        email = self.input_str("邮箱: ")
        join_date = self.input_date("入职日期 (YYYY-MM-DD): ")
        base_salary = self.input_float("基本薪资 (默认5000): ", default=5000)

        employee = self.employee_service.add_employee(
            name=name,
            gender=gender,
            department=department,
            position=position,
            phone=phone,
            email=email,
            join_date=join_date,
            base_salary=base_salary,
        )

        if employee:
            print(f"\n  ✓ 员工添加成功！员工编号: {employee.employee_no}")
        else:
            print("\n  ✗ 员工添加失败！")

    def list_employees(self):
        self.print_header("员工列表")
        employees = self.employee_service.get_all_employees()

        if not employees:
            print("\n  暂无员工数据！")
            return

        print(f"\n共 {len(employees)} 名员工\n")
        print(f"{'编号':<10}{'姓名':<10}{'性别':<6}{'部门':<12}{'职位':<10}{'状态':<8}{'薪资':<12}")
        print("-" * 70)

        for emp in employees:
            print(
                f"{emp.employee_no:<10}{emp.name:<10}{emp.gender:<6}"
                f"{emp.department:<12}{emp.position:<10}{emp.status:<8}{emp.base_salary:<12.2f}"
            )

    def search_employees(self):
        self.print_header("搜索员工")
        keyword = self.input_str("请输入搜索关键词（姓名/编号/部门/电话）: ")
        employees = self.employee_service.search_employees(keyword)

        if not employees:
            print(f"\n  未找到匹配 '{keyword}' 的员工！")
            return

        print(f"\n找到 {len(employees)} 名员工\n")
        print(f"{'编号':<10}{'姓名':<10}{'性别':<6}{'部门':<12}{'职位':<10}{'状态':<8}")
        print("-" * 60)

        for emp in employees:
            print(
                f"{emp.employee_no:<10}{emp.name:<10}{emp.gender:<6}"
                f"{emp.department:<12}{emp.position:<10}{emp.status:<8}"
            )

    def update_employee(self):
        self.print_header("更新员工信息")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到编号为 {emp_no} 的员工！")
            return

        print(f"\n当前信息:")
        print(f"  姓名: {employee.name}")
        print(f"  性别: {employee.gender}")
        print(f"  部门: {employee.department}")
        print(f"  职位: {employee.position}")
        print(f"  电话: {employee.phone}")
        print(f"  邮箱: {employee.email}")
        print(f"  状态: {employee.status}")
        print(f"\n留空保持原值\n")

        name = self.input_str(f"新姓名 ({employee.name}): ", allow_empty=True)
        gender = self.input_str(f"新性别 ({employee.gender}): ", allow_empty=True)
        department = self.input_str(f"新部门 ({employee.department}): ", allow_empty=True)
        position = self.input_str(f"新职位 ({employee.position}): ", allow_empty=True)
        phone = self.input_str(f"新电话 ({employee.phone}): ", allow_empty=True)
        email = self.input_str(f"新邮箱 ({employee.email}): ", allow_empty=True)
        status = self.input_str(f"新状态 (在职/离职) ({employee.status}): ", allow_empty=True)

        updates = {}
        if name:
            updates["name"] = name
        if gender:
            updates["gender"] = gender
        if department:
            updates["department"] = department
        if position:
            updates["position"] = position
        if phone:
            updates["phone"] = phone
        if email:
            updates["email"] = email
        if status:
            updates["status"] = status

        if updates:
            if self.employee_service.update_employee(employee.id, **updates):
                print(f"\n  ✓ 员工信息更新成功！")
            else:
                print(f"\n  ✗ 更新失败！")
        else:
            print("\n  没有任何更改。")

    def delete_employee(self):
        self.print_header("删除员工")
        emp_no = self.input_str("请输入要删除的员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到编号为 {emp_no} 的员工！")
            return

        confirm = self.input_str(f"确认删除员工 {employee.name}? (Y/N): ").upper()
        if confirm == "Y":
            if self.employee_service.delete_employee(employee.id):
                print(f"\n  ✓ 员工 {employee.name} 已删除！")
            else:
                print(f"\n  ✗ 删除失败！")
        else:
            print("\n  操作已取消。")

    def list_by_department(self):
        self.print_header("按部门查看员工")
        departments = self.config_service.get_departments()

        print("\n可用部门:")
        for i, dept in enumerate(departments, 1):
            print(f"  {i}. {dept}")

        choice = self.input_int("请选择部门编号: ")
        if 1 <= choice <= len(departments):
            dept = departments[choice - 1]
            employees = self.employee_service.get_employees_by_department(dept)

            if not employees:
                print(f"\n  {dept} 暂无员工！")
                return

            print(f"\n【{dept}】共 {len(employees)} 人\n")
            print(f"{'编号':<10}{'姓名':<10}{'职位':<10}{'状态':<8}")
            print("-" * 40)

            for emp in employees:
                print(f"{emp.employee_no:<10}{emp.name:<10}{emp.position:<10}{emp.status:<8}")
        else:
            print("\n  无效的选择！")

    def filter_employees_ui(self):
        self.print_header("多条件筛选员工")
        print("\n请输入筛选条件（留空表示不限制）\n")

        departments = self.config_service.get_departments()
        positions = self.config_service.get_positions()

        print(f"可用部门: {', '.join(departments)}")
        print(f"可用职位: {', '.join(positions)}")
        print()

        department = self.input_str("部门: ", allow_empty=True)
        employee_no = self.input_str("工号: ", allow_empty=True)
        name = self.input_str("姓名: ", allow_empty=True)
        status = self.input_str("状态 (在职/离职): ", allow_empty=True)
        position = self.input_str("职位: ", allow_empty=True)

        employees = self.employee_service.filter_employees(
            department=department if department else None,
            employee_no=employee_no if employee_no else None,
            name=name if name else None,
            status=status if status else None,
            position=position if position else None,
        )

        if not employees:
            print("\n  未找到符合条件的员工！")
            return

        print(f"\n找到 {len(employees)} 名员工\n")
        print(f"{'编号':<10}{'姓名':<10}{'性别':<6}{'部门':<12}{'职位':<10}{'状态':<8}{'薪资':<12}")
        print("-" * 70)

        for emp in employees:
            print(
                f"{emp.employee_no:<10}{emp.name:<10}{emp.gender:<6}"
                f"{emp.department:<12}{emp.position:<10}{emp.status:<8}{emp.base_salary:<12.2f}"
            )

    def batch_import_employees(self):
        self.print_header("批量导入员工")
        print("\n1. 从 CSV 文件导入")
        print("2. 从 TXT 文件导入")
        print("3. 查看导入格式说明")
        print("0. 取消")

        choice = self.input_int("\n请选择 [0-3]: ")

        if choice == 0:
            print("\n  操作已取消。")
            return
        elif choice == 3:
            print("\n" + "=" * 60)
            print(self.employee_service.get_import_template())
            print("=" * 60)
            return

        file_path = self.input_str("请输入文件完整路径: ")

        if choice == 1:
            success, fail, errors = self.employee_service.batch_import_from_csv(file_path)
        elif choice == 2:
            delimiter = self.input_str("请输入分隔符 (默认逗号): ", allow_empty=True) or ","
            success, fail, errors = self.employee_service.batch_import_from_txt(file_path, delimiter)
        else:
            print("\n  无效的选择！")
            return

        print(f"\n  导入完成!")
        print(f"    成功: {success} 条")
        print(f"    失败: {fail} 条")

        if errors:
            print(f"\n  错误详情:")
            for err in errors[:10]:
                print(f"    - {err}")
            if len(errors) > 10:
                print(f"    ... 还有 {len(errors) - 10} 条错误")

    def export_employees_report(self):
        self.print_header("导出员工报表")
        print("\n1. 导出所有员工")
        print("2. 按筛选条件导出")
        print("0. 取消")

        choice = self.input_int("\n请选择 [0-2]: ")

        if choice == 0:
            print("\n  操作已取消。")
            return

        employees = None
        if choice == 2:
            department = self.input_str("筛选部门 (留空不限制): ", allow_empty=True)
            employee_no = self.input_str("筛选工号 (留空不限制): ", allow_empty=True)
            name = self.input_str("筛选姓名 (留空不限制): ", allow_empty=True)
            status = self.input_str("筛选状态 (在职/离职, 留空不限制): ", allow_empty=True)

            employees = self.employee_service.filter_employees(
                department=department if department else None,
                employee_no=employee_no if employee_no else None,
                name=name if name else None,
                status=status if status else None,
            )

            if not employees:
                print("\n  未找到符合条件的员工！")
                return

            print(f"\n  找到 {len(employees)} 名员工待导出")

        print("\n1. 导出为 CSV 格式")
        print("2. 导出为 TXT 格式")
        format_choice = self.input_int("请选择格式 [1-2]: ")

        default_name = f"employees_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = self.input_str(f"请输入文件名 (默认 {default_name}): ", allow_empty=True) or default_name

        from src.config.settings import DATA_DIR
        import os

        if format_choice == 1:
            file_path = os.path.join(DATA_DIR, f"{filename}.csv")
            result = self.employee_service.export_to_csv(file_path, employees)
        elif format_choice == 2:
            delimiter = self.input_str("请输入分隔符 (默认逗号): ", allow_empty=True) or ","
            file_path = os.path.join(DATA_DIR, f"{filename}.txt")
            result = self.employee_service.export_to_txt(file_path, employees, delimiter)
        else:
            print("\n  无效的选择！")
            return

        if result:
            print(f"\n  ✓ 导出成功！文件路径:")
            print(f"    {file_path}")
        else:
            print(f"\n  ✗ 导出失败！")

    def attendance_menu(self):
        while True:
            self.print_header("考勤打卡")
            self.print_menu({
                "1": "上班打卡",
                "2": "下班打卡",
                "3": "查看今日考勤",
                "4": "查看月度考勤",
                "5": "标记缺勤",
                "0": "返回主菜单",
            })

            choice = self.input_int("请选择操作 [0-5]: ")

            if choice == 0:
                break
            elif choice == 1:
                self.clock_in()
            elif choice == 2:
                self.clock_out()
            elif choice == 3:
                self.view_today_attendance()
            elif choice == 4:
                self.view_monthly_attendance()
            elif choice == 5:
                self.mark_absent()
            else:
                print("  无效的选择！")
            self.wait_enter()

    def clock_in(self):
        self.print_header("上班打卡")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        record = self.attendance_service.clock_in(employee.id)
        if record:
            status = "迟到" if record.is_late else "正常"
            print(f"\n  ✓ {employee.name} 上班打卡成功！")
            print(f"    打卡时间: {record.clock_in_time}")
            print(f"    打卡状态: {status}")
        else:
            print(f"\n  ✗ 打卡失败，可能已打卡！")

    def clock_out(self):
        self.print_header("下班打卡")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        record = self.attendance_service.clock_out(employee.id)
        if record:
            status = "早退" if record.is_early_leave else "正常"
            print(f"\n  ✓ {employee.name} 下班打卡成功！")
            print(f"    打卡时间: {record.clock_out_time}")
            print(f"    打卡状态: {status}")
            if record.overtime_hours > 0:
                print(f"    加班时长: {record.overtime_hours} 小时")
        else:
            print(f"\n  ✗ 打卡失败，请先上班打卡！")

    def view_today_attendance(self):
        self.print_header("今日考勤")
        today = datetime.now().strftime("%Y-%m-%d")
        records = self.attendance_service.get_records_by_date(today)

        if not records:
            print("\n  今日暂无考勤记录！")
            return

        print(f"\n日期: {today}")
        print(f"共 {len(records)} 条记录\n")
        print(f"{'姓名':<10}{'上班时间':<12}{'下班时间':<12}{'状态':<12}{'加班(h)':<10}")
        print("-" * 60)

        for r in records:
            print(
                f"{r.employee_name:<10}{r.clock_in_time or '-':<12}"
                f"{r.clock_out_time or '-':<12}{r.status:<12}{r.overtime_hours:<10.1f}"
            )

    def view_monthly_attendance(self):
        self.print_header("月度考勤")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        stats = self.attendance_service.calculate_monthly_stats(employee.id, month)
        records = self.attendance_service.get_records_by_month(employee.id, month)

        print(f"\n【{employee.name}】{month} 考勤统计")
        print("-" * 40)
        print(f"  出勤天数: {stats['total_days']} 天")
        print(f"  正常天数: {stats['normal_days']} 天")
        print(f"  迟到次数: {stats['late_days']} 次")
        print(f"  早退次数: {stats['early_leave_days']} 次")
        print(f"  缺勤天数: {stats['absence_days']} 天")
        print(f"  加班时长: {stats['overtime_hours']} 小时")

        if records:
            print(f"\n详细记录 ({len(records)} 条):")
            print(f"{'日期':<12}{'上班':<10}{'下班':<10}{'状态':<10}")
            print("-" * 44)
            for r in records:
                print(
                    f"{r.date:<12}{r.clock_in_time or '-':<10}"
                    f"{r.clock_out_time or '-':<10}{r.status:<10}"
                )

    def mark_absent(self):
        self.print_header("标记缺勤")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        date = self.input_date("请输入缺勤日期 (YYYY-MM-DD): ")
        remark = self.input_str("备注 (可空): ", allow_empty=True)

        record = self.attendance_service.mark_absent(employee.id, date, remark)
        if record:
            print(f"\n  ✓ {employee.name} {date} 已标记为缺勤！")
        else:
            print(f"\n  ✗ 标记失败！")

    def leave_menu(self):
        while True:
            self.print_header("请假审批")
            pending_count = self.leave_service.count_pending_applications()

            if pending_count > 0:
                print(f"\n  【提示】有 {pending_count} 条请假申请待审批！")

            self.print_menu({
                "1": "申请请假",
                "2": "查看我的请假",
                "3": "待审批列表",
                "4": "审批请假",
                "5": "取消申请",
                "0": "返回主菜单",
            })

            choice = self.input_int("请选择操作 [0-5]: ")

            if choice == 0:
                break
            elif choice == 1:
                self.apply_leave()
            elif choice == 2:
                self.view_my_leave()
            elif choice == 3:
                self.view_pending_leave()
            elif choice == 4:
                self.approve_leave()
            elif choice == 5:
                self.cancel_leave()
            else:
                print("  无效的选择！")
            self.wait_enter()

    def apply_leave(self):
        self.print_header("申请请假")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        leave_types = self.config_service.get_leave_types()
        print(f"\n可用请假类型: {', '.join(leave_types)}")

        leave_type = self.input_str("请假类型: ")
        if leave_type not in leave_types:
            print(f"\n  无效的请假类型！")
            return

        start_date = self.input_date("开始日期 (YYYY-MM-DD): ")
        end_date = self.input_date("结束日期 (YYYY-MM-DD): ")
        reason = self.input_str("请假原因: ")

        application = self.leave_service.apply_leave(
            emp_id=employee.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        if application:
            print(f"\n  ✓ 请假申请提交成功！")
            print(f"    请假类型: {application.leave_type}")
            print(f"    请假时间: {application.start_date} ~ {application.end_date}")
            print(f"    请假天数: {application.total_days} 天")
            print(f"    当前状态: {application.status}")
        else:
            print(f"\n  ✗ 申请提交失败！")

    def view_my_leave(self):
        self.print_header("我的请假记录")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        applications = self.leave_service.get_applications_by_employee(employee.id)

        if not applications:
            print(f"\n  {employee.name} 暂无请假记录！")
            return

        print(f"\n共 {len(applications)} 条记录\n")
        print(f"{'类型':<10}{'开始日期':<12}{'结束日期':<12}{'天数':<8}{'状态':<10}")
        print("-" * 55)

        for app in applications:
            print(
                f"{app.leave_type:<10}{app.start_date:<12}"
                f"{app.end_date:<12}{app.total_days:<8}{app.status:<10}"
            )

    def view_pending_leave(self):
        self.print_header("待审批请假")
        applications = self.leave_service.get_pending_applications()

        if not applications:
            print("\n  暂无待审批的请假申请！")
            return

        print(f"\n共 {len(applications)} 条待审批申请\n")
        print(f"{'申请人':<10}{'类型':<10}{'开始日期':<12}{'结束日期':<12}{'天数':<8}")
        print("-" * 55)

        for app in applications:
            print(
                f"{app.employee_name:<10}{app.leave_type:<10}"
                f"{app.start_date:<12}{app.end_date:<12}{app.total_days:<8}"
            )
        print("\n  提示: 使用请假编号进行审批")

    def approve_leave(self):
        self.print_header("审批请假")
        applications = self.leave_service.get_pending_applications()

        if not applications:
            print("\n  暂无待审批的请假申请！")
            return

        print(f"\n共 {len(applications)} 条待审批申请\n")
        for i, app in enumerate(applications, 1):
            print(f"  {i}. {app.employee_name} - {app.leave_type} ({app.start_date}~{app.end_date}) - {app.reason}")

        choice = self.input_int("\n请选择要审批的申请编号 (0取消): ")
        if choice == 0:
            print("\n  操作已取消。")
            return

        if 1 <= choice <= len(applications):
            app = applications[choice - 1]
            action = self.input_str(f"\n请选择操作 (A批准/R拒绝): ").upper()
            approver = self.input_str("审批人姓名: ")
            remark = self.input_str("审批备注 (可空): ", allow_empty=True)

            if action == "A":
                result = self.leave_service.approve(app.id, approver, remark)
                if result:
                    print(f"\n  ✓ 已批准 {app.employee_name} 的请假申请！")
            elif action == "R":
                result = self.leave_service.reject(app.id, approver, remark)
                if result:
                    print(f"\n  ✓ 已拒绝 {app.employee_name} 的请假申请！")
            else:
                print("\n  无效的操作！")
        else:
            print("\n  无效的选择！")

    def cancel_leave(self):
        self.print_header("取消请假申请")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        pending_apps = [
            app for app in self.leave_service.get_applications_by_employee(employee.id)
            if app.status == "待审批"
        ]

        if not pending_apps:
            print(f"\n  {employee.name} 没有待审批的请假申请！")
            return

        print(f"\n待审批申请:")
        for i, app in enumerate(pending_apps, 1):
            print(f"  {i}. {app.leave_type} ({app.start_date}~{app.end_date})")

        choice = self.input_int("\n请选择要取消的申请编号 (0取消): ")
        if choice == 0:
            print("\n  操作已取消。")
            return

        if 1 <= choice <= len(pending_apps):
            app = pending_apps[choice - 1]
            confirm = self.input_str(f"确认取消该申请? (Y/N): ").upper()
            if confirm == "Y":
                if self.leave_service.cancel(app.id):
                    print(f"\n  ✓ 申请已取消！")
                else:
                    print(f"\n  ✗ 取消失败！")
        else:
            print("\n  无效的选择！")

    def salary_menu(self):
        while True:
            self.print_header("薪资核算")
            self.print_menu({
                "1": "生成月度薪资",
                "2": "查看薪资记录",
                "3": "发放薪资",
                "4": "薪资统计",
                "0": "返回主菜单",
            })

            choice = self.input_int("请选择操作 [0-4]: ")

            if choice == 0:
                break
            elif choice == 1:
                self.generate_monthly_salary()
            elif choice == 2:
                self.view_salary_records()
            elif choice == 3:
                self.pay_salary()
            elif choice == 4:
                self.view_salary_summary()
            else:
                print("  无效的选择！")
            self.wait_enter()

    def generate_monthly_salary(self):
        self.print_header("生成月度薪资")
        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        existing = self.salary_service.get_records_by_month(month)
        if existing:
            confirm = self.input_str(f"该月已存在薪资记录，重新生成? (Y/N): ").upper()
            if confirm != "Y":
                print("\n  操作已取消。")
                return

        records = self.salary_service.generate_monthly_salary(month)

        if records:
            print(f"\n  ✓ 已为 {len(records)} 名员工生成 {month} 薪资！")
            total = sum(r.net_salary for r in records)
            print(f"    薪资总额: {total:.2f} 元")
        else:
            print(f"\n  未生成薪资记录，可能已全部生成或无在职员工。")

    def view_salary_records(self):
        self.print_header("查看薪资记录")
        print("\n1. 按月份查看")
        print("2. 按员工查看")
        choice = self.input_int("请选择 [1-2]: ")

        if choice == 1:
            current_month = datetime.now().strftime("%Y-%m")
            month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
            month = month or current_month

            records = self.salary_service.get_records_by_month(month)
            self._print_salary_records(records, month)

        elif choice == 2:
            emp_no = self.input_str("请输入员工编号: ")
            employee = self.employee_service.get_employee_by_no(emp_no)

            if not employee:
                print(f"\n  未找到员工编号 {emp_no}！")
                return

            records = self.salary_service.get_records_by_employee(employee.id)
            self._print_salary_records(records, f"{employee.name}")
        else:
            print("\n  无效的选择！")

    def _print_salary_records(self, records, title):
        if not records:
            print(f"\n  {title} 暂无薪资记录！")
            return

        print(f"\n共 {len(records)} 条记录\n")
        print(f"{'月份':<10}{'姓名':<10}{'部门':<12}{'基本薪资':<12}{'实发薪资':<12}{'状态':<10}")
        print("-" * 70)

        for r in records:
            print(
                f"{r.month:<10}{r.employee_name:<10}{r.department:<12}"
                f"{r.base_salary:<12.2f}{r.net_salary:<12.2f}{r.status:<10}"
            )

    def pay_salary(self):
        self.print_header("发放薪资")
        print("\n1. 单个发放")
        print("2. 批量发放")
        choice = self.input_int("请选择 [1-2]: ")

        if choice == 1:
            current_month = datetime.now().strftime("%Y-%m")
            month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
            month = month or current_month

            records = self.salary_service.get_records_by_month(month)
            unpaid = [r for r in records if r.status == "未发放"]

            if not unpaid:
                print(f"\n  {month} 没有待发放的薪资！")
                return

            print(f"\n待发放记录 ({len(unpaid)} 条):")
            for i, r in enumerate(unpaid, 1):
                print(f"  {i}. {r.employee_name} - {r.net_salary:.2f} 元")

            idx = self.input_int("\n请选择编号 (0取消): ")
            if 1 <= idx <= len(unpaid):
                record = unpaid[idx - 1]
                confirm = self.input_str(f"确认发放 {record.employee_name} {record.net_salary:.2f} 元? (Y/N): ").upper()
                if confirm == "Y":
                    if self.salary_service.pay_salary(record.id):
                        print(f"\n  ✓ 发放成功！")
                    else:
                        print(f"\n  ✗ 发放失败！")
            else:
                print("\n  操作已取消。")

        elif choice == 2:
            current_month = datetime.now().strftime("%Y-%m")
            month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
            month = month or current_month

            confirm = self.input_str(f"确认批量发放 {month} 所有未发薪资? (Y/N): ").upper()
            if confirm == "Y":
                paid = self.salary_service.batch_pay_salary(month)
                print(f"\n  ✓ 已发放 {len(paid)} 条薪资记录！")
        else:
            print("\n  无效的选择！")

    def view_salary_summary(self):
        self.print_header("薪资统计")
        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        summary = self.salary_service.get_monthly_summary(month)

        print(f"\n【{month} 薪资统计】")
        print("-" * 40)
        print(f"  员工数量: {summary['total_employees']} 人")
        print(f"  基本薪资总额: {summary['total_base_salary']:.2f} 元")
        print(f"  加班薪资总额: {summary['total_overtime_pay']:.2f} 元")
        print(f"  奖金总额: {summary['total_bonus']:.2f} 元")
        print(f"  扣款总额: {summary['total_deductions']:.2f} 元")
        print(f"  实发薪资总额: {summary['total_net_salary']:.2f} 元")
        print(f"  平均薪资: {summary['average_salary']:.2f} 元")
        print(f"\n  已发放: {summary['paid_count']} 人")
        print(f"  未发放: {summary['unpaid_count']} 人")

    def report_menu(self):
        while True:
            self.print_header("数据报表")
            self.print_menu({
                "1": "仪表盘概览",
                "2": "员工统计报表",
                "3": "考勤统计报表",
                "4": "请假统计报表",
                "5": "薪资统计报表",
                "6": "员工个人考勤",
                "7": "员工个人薪资",
                "0": "返回主菜单",
            })

            choice = self.input_int("请选择操作 [0-7]: ")

            if choice == 0:
                break
            elif choice == 1:
                self.show_dashboard_report()
            elif choice == 2:
                self.show_employee_report()
            elif choice == 3:
                self.show_attendance_report()
            elif choice == 4:
                self.show_leave_report()
            elif choice == 5:
                self.show_salary_report()
            elif choice == 6:
                self.show_employee_attendance_detail()
            elif choice == 7:
                self.show_employee_salary_detail()
            else:
                print("  无效的选择！")
            self.wait_enter()

    def show_dashboard_report(self):
        self.print_header("仪表盘概览")
        report = self.report_service.generate_dashboard_report()

        print(f"\n  今日: {report['today']}")
        print(f"  当前月份: {report['current_month']}")
        print("\n【员工数据】")
        print(f"  总员工数: {report['employee_summary']['total']} 人")
        print(f"  在职员工: {report['employee_summary']['active']} 人")

        print("\n【今日考勤】")
        print(f"  打卡人数: {report['attendance_today']['total_punched']} 人")
        print(f"  迟到人数: {report['attendance_today']['late']} 人")

        print("\n【本月考勤】")
        print(f"  出勤率: {report['attendance_monthly']['attendance_rate']}%")
        print(f"  迟到天数: {report['attendance_monthly']['late_days']} 天")
        print(f"  加班时长: {report['attendance_monthly']['overtime_hours']} 小时")

        print("\n【请假数据】")
        print(f"  待审批: {report['leave_summary']['pending_approval']} 条")
        print(f"  本月申请: {report['leave_summary']['total_month_applications']} 条")

        print("\n【薪资数据】")
        salary = report["salary_summary"]
        print(f"  本月薪资总额: {salary.get('total_net_salary', 0):.2f} 元")
        print(f"  发放状态: 已发 {salary.get('paid_count', 0)} / {salary.get('total_employees', 0)}")

    def show_employee_report(self):
        self.print_header("员工统计报表")
        report = self.report_service.generate_employee_report()

        print(f"\n  员工总数: {report['total_employees']} 人")
        print(f"  基本薪资总额: {report['total_base_salary']:.2f} 元")
        print(f"  平均基本薪资: {report['average_base_salary']:.2f} 元")

        print("\n【按部门】")
        for dept, count in report["by_department"].items():
            print(f"  {dept}: {count} 人")

        print("\n【按职位】")
        for pos, count in report["by_position"].items():
            print(f"  {pos}: {count} 人")

        print("\n【按状态】")
        for status, count in report["by_status"].items():
            print(f"  {status}: {count} 人")

    def show_attendance_report(self):
        self.print_header("考勤统计报表")
        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        report = self.report_service.generate_attendance_report(month)

        print(f"\n【{month} 考勤统计】")
        print("-" * 40)
        print(f"  考勤记录数: {report['total_days_recorded']} 条")
        print(f"  迟到天数: {report['total_late_days']} 天")
        print(f"  早退天数: {report['total_early_leave_days']} 天")
        print(f"  缺勤天数: {report['total_absence_days']} 天")
        print(f"  加班总时长: {report['total_overtime_hours']} 小时")
        print(f"  整体出勤率: {report['attendance_rate']}%")

        print("\n【按部门】")
        print(f"{'部门':<12}{'员工数':<8}{'迟到':<8}{'早退':<8}{'缺勤':<8}")
        print("-" * 50)
        for dept, stats in report["by_department"].items():
            print(
                f"{dept:<12}{stats['employee_count']:<8}"
                f"{stats['late_days']:<8}{stats['early_leave_days']:<8}{stats['absence_days']:<8}"
            )

    def show_leave_report(self):
        self.print_header("请假统计报表")
        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        report = self.report_service.generate_leave_report(month)

        print(f"\n【{month} 请假统计】")
        print("-" * 40)
        print(f"  请假申请总数: {report['total_applications']} 条")

        print("\n【按类型】")
        for leave_type, stats in report["by_type"].items():
            print(f"  {leave_type}: {stats['count']} 次 ({stats['total_days']} 天)")

        print("\n【按状态】")
        for status, count in report["by_status"].items():
            print(f"  {status}: {count} 条")

        print("\n【按部门】")
        for dept, stats in report["by_department"].items():
            print(f"  {dept}: {stats['total_days']} 天")

    def show_salary_report(self):
        self.print_header("薪资统计报表")
        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        report = self.report_service.generate_salary_report(month)
        summary = report["summary"]

        print(f"\n【{month} 薪资汇总】")
        print("-" * 40)
        print(f"  员工数: {summary['total_employees']} 人")
        print(f"  基本薪资总额: {summary['total_base_salary']:.2f} 元")
        print(f"  加班薪资: {summary['total_overtime_pay']:.2f} 元")
        print(f"  奖金总额: {summary['total_bonus']:.2f} 元")
        print(f"  扣款总额: {summary['total_deductions']:.2f} 元")
        print(f"  实发总额: {summary['total_net_salary']:.2f} 元")
        print(f"  平均薪资: {summary['average_salary']:.2f} 元")
        print(f"  发放状态: {summary['paid_count']}/{summary['total_employees']}")

        print("\n【按部门】")
        print(f"{'部门':<12}{'员工数':<8}{'总额':<15}{'平均':<15}")
        print("-" * 55)
        for dept, stats in report["by_department"].items():
            print(
                f"{dept:<12}{stats['employee_count']:<8}"
                f"{stats['total_salary']:<15.2f}{stats['average_salary']:<15.2f}"
            )

    def show_employee_attendance_detail(self):
        self.print_header("员工个人考勤")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        report = self.report_service.generate_employee_attendance_report(employee.id, month)

        if "error" in report:
            print(f"\n  {report['error']}")
            return

        emp = report["employee"]
        stats = report["attendance_stats"]

        print(f"\n【{emp['name']} - {month}】")
        print(f"  部门: {emp['department']} | 职位: {emp['position']}")
        print("-" * 40)
        print(f"  出勤天数: {stats['total_days']} 天")
        print(f"  正常天数: {stats['normal_days']} 天")
        print(f"  迟到天数: {stats['late_days']} 天")
        print(f"  早退天数: {stats['early_leave_days']} 天")
        print(f"  缺勤天数: {stats['absence_days']} 天")
        print(f"  加班时长: {stats['overtime_hours']} 小时")
        print(f"  请假天数: {report['leave_days']} 天")

        if report["records"]:
            show_detail = self.input_str("\n查看详细记录? (Y/N): ").upper()
            if show_detail == "Y":
                print(f"\n{'日期':<12}{'上班':<10}{'下班':<10}{'状态':<10}{'加班':<8}")
                print("-" * 52)
                for r in report["records"]:
                    status = r["status"]
                    if r["is_late"]:
                        status += "(迟)"
                    if r["is_early_leave"]:
                        status += "(早)"
                    print(
                        f"{r['date']:<12}{r['clock_in'] or '-':<10}"
                        f"{r['clock_out'] or '-':<10}{status:<10}{r['overtime_hours']:<8}"
                    )

    def show_employee_salary_detail(self):
        self.print_header("员工个人薪资")
        emp_no = self.input_str("请输入员工编号: ")
        employee = self.employee_service.get_employee_by_no(emp_no)

        if not employee:
            print(f"\n  未找到员工编号 {emp_no}！")
            return

        current_month = datetime.now().strftime("%Y-%m")
        month = self.input_month(f"请输入月份 (YYYY-MM) [{current_month}]: ", allow_empty=True)
        month = month or current_month

        report = self.report_service.generate_employee_salary_report(employee.id, month)

        if "error" in report:
            print(f"\n  {report['error']}")
            return

        emp = report["employee"]
        sal = report["salary_details"]

        print(f"\n【{emp['name']} - {month} 薪资明细】")
        print(f"  部门: {emp['department']} | 职位: {emp['position']}")
        print("-" * 40)
        print(f"  基本薪资: {sal['base_salary']:.2f} 元")
        print(f"  加班薪资: + {sal['overtime_pay']:.2f} 元")
        print(f"  奖金:     + {sal['bonus']:.2f} 元")
        print(f"  迟到扣款: - {sal['late_deduction']:.2f} 元")
        print(f"  早退扣款: - {sal['early_leave_deduction']:.2f} 元")
        print(f"  缺勤扣款: - {sal['absence_deduction']:.2f} 元")
        print(f"  请假扣款: - {sal['leave_deduction']:.2f} 元")
        print("-" * 40)
        print(f"  实发薪资: {sal['net_salary']:.2f} 元")
        print(f"\n  状态: {report['status']}")
        if report["paid_at"]:
            print(f"  发放时间: {report['paid_at']}")

    def config_menu(self):
        while True:
            self.print_header("系统配置")
            self.print_menu({
                "1": "查看当前配置",
                "2": "部门管理",
                "3": "职位管理",
                "4": "请假类型管理",
                "5": "薪资配置",
                "6": "工作时间配置",
                "7": "重置配置",
                "0": "返回主菜单",
            })

            choice = self.input_int("请选择操作 [0-7]: ")

            if choice == 0:
                break
            elif choice == 1:
                self.view_current_config()
            elif choice == 2:
                self.manage_departments()
            elif choice == 3:
                self.manage_positions()
            elif choice == 4:
                self.manage_leave_types()
            elif choice == 5:
                self.configure_salary()
            elif choice == 6:
                self.configure_work_hours()
            elif choice == 7:
                self.reset_config()
            else:
                print("  无效的选择！")
            self.wait_enter()

    def view_current_config(self):
        self.print_header("当前系统配置")
        config = self.config_service.get_all_config()

        print("\n【系统信息】")
        print(f"  系统名称: {config['system']['name']}")
        print(f"  版本: {config['system']['version']}")

        print("\n【工作时间】")
        work = config["work_hours"]
        print(f"  上班时间: {work['work_start_time']}")
        print(f"  下班时间: {work['work_end_time']}")
        print(f"  迟到阈值: {work['late_threshold_minutes']} 分钟")

        print("\n【薪资配置】")
        sal = config["salary"]
        print(f"  默认基本薪资: {sal['default_base_salary']} 元")
        print(f"  加班倍率: {sal['overtime_rate']}x")
        print(f"  迟到扣款: {sal['late_deduction']} 元/次")
        print(f"  早退扣款: {sal['early_leave_deduction']} 元/次")
        print(f"  缺勤扣款: {sal['absence_deduction']} 元/天")

        print("\n【部门列表】", ", ".join(config["departments"]))
        print("【职位列表】", ", ".join(config["positions"]))
        print("【请假类型】", ", ".join(config["leave_types"]))

    def manage_departments(self):
        while True:
            self.print_header("部门管理")
            departments = self.config_service.get_departments()

            print(f"\n当前部门 ({len(departments)} 个):")
            for i, dept in enumerate(departments, 1):
                print(f"  {i}. {dept}")

            self.print_menu({
                "1": "添加部门",
                "2": "删除部门",
                "0": "返回",
            })

            choice = self.input_int("请选择 [0-2]: ")

            if choice == 0:
                break
            elif choice == 1:
                name = self.input_str("请输入新部门名称: ")
                if self.config_service.add_department(name):
                    print(f"\n  ✓ 部门 {name} 添加成功！")
                else:
                    print(f"\n  ✗ 添加失败，部门可能已存在！")
            elif choice == 2:
                idx = self.input_int("请输入要删除的部门编号: ")
                if 1 <= idx <= len(departments):
                    dept = departments[idx - 1]
                    confirm = self.input_str(f"确认删除部门 {dept}? (Y/N): ").upper()
                    if confirm == "Y":
                        if self.config_service.remove_department(dept):
                            print(f"\n  ✓ 部门 {dept} 已删除！")
                        else:
                            print(f"\n  ✗ 删除失败！")
                else:
                    print("\n  无效的编号！")
            self.wait_enter()

    def manage_positions(self):
        while True:
            self.print_header("职位管理")
            positions = self.config_service.get_positions()

            print(f"\n当前职位 ({len(positions)} 个):")
            for i, pos in enumerate(positions, 1):
                print(f"  {i}. {pos}")

            self.print_menu({
                "1": "添加职位",
                "2": "删除职位",
                "0": "返回",
            })

            choice = self.input_int("请选择 [0-2]: ")

            if choice == 0:
                break
            elif choice == 1:
                name = self.input_str("请输入新职位名称: ")
                if self.config_service.add_position(name):
                    print(f"\n  ✓ 职位 {name} 添加成功！")
                else:
                    print(f"\n  ✗ 添加失败，职位可能已存在！")
            elif choice == 2:
                idx = self.input_int("请输入要删除的职位编号: ")
                if 1 <= idx <= len(positions):
                    pos = positions[idx - 1]
                    confirm = self.input_str(f"确认删除职位 {pos}? (Y/N): ").upper()
                    if confirm == "Y":
                        if self.config_service.remove_position(pos):
                            print(f"\n  ✓ 职位 {pos} 已删除！")
                        else:
                            print(f"\n  ✗ 删除失败！")
                else:
                    print("\n  无效的编号！")
            self.wait_enter()

    def manage_leave_types(self):
        while True:
            self.print_header("请假类型管理")
            types = self.config_service.get_leave_types()

            print(f"\n当前类型 ({len(types)} 个):")
            for i, t in enumerate(types, 1):
                print(f"  {i}. {t}")

            self.print_menu({
                "1": "添加类型",
                "2": "删除类型",
                "0": "返回",
            })

            choice = self.input_int("请选择 [0-2]: ")

            if choice == 0:
                break
            elif choice == 1:
                name = self.input_str("请输入新请假类型: ")
                if self.config_service.add_leave_type(name):
                    print(f"\n  ✓ 请假类型 {name} 添加成功！")
                else:
                    print(f"\n  ✗ 添加失败，类型可能已存在！")
            elif choice == 2:
                idx = self.input_int("请输入要删除的类型编号: ")
                if 1 <= idx <= len(types):
                    t = types[idx - 1]
                    confirm = self.input_str(f"确认删除类型 {t}? (Y/N): ").upper()
                    if confirm == "Y":
                        if self.config_service.remove_leave_type(t):
                            print(f"\n  ✓ 类型 {t} 已删除！")
                        else:
                            print(f"\n  ✗ 删除失败！")
                else:
                    print("\n  无效的编号！")
            self.wait_enter()

    def configure_salary(self):
        self.print_header("薪资配置")
        current = self.config_service.get_salary_config()

        print(f"\n当前配置 (留空保持原值):")
        print(f"  1. 默认基本薪资: {current['default_base_salary']} 元")
        print(f"  2. 加班倍率: {current['overtime_rate']}x")
        print(f"  3. 迟到扣款: {current['late_deduction']} 元/次")
        print(f"  4. 早退扣款: {current['early_leave_deduction']} 元/次")
        print(f"  5. 缺勤扣款: {current['absence_deduction']} 元/天")

        print("\n请输入新值 (留空保持不变):")
        default_salary = self.input_float("默认基本薪资: ", default=None)
        overtime_rate = self.input_float("加班倍率: ", default=None)
        late_ded = self.input_float("迟到扣款: ", default=None)
        early_ded = self.input_float("早退扣款: ", default=None)
        absence_ded = self.input_float("缺勤扣款: ", default=None)

        if (
            default_salary is None
            and overtime_rate is None
            and late_ded is None
            and early_ded is None
            and absence_ded is None
        ):
            print("\n  没有任何更改。")
            return

        if self.config_service.set_salary_config(
            default_base_salary=default_salary,
            overtime_rate=overtime_rate,
            late_deduction=late_ded,
            early_leave_deduction=early_ded,
            absence_deduction=absence_ded,
        ):
            print(f"\n  ✓ 薪资配置已更新！")
        else:
            print(f"\n  ✗ 更新失败！")

    def configure_work_hours(self):
        self.print_header("工作时间配置")
        current = self.config_service.get_work_hours()

        print(f"\n当前配置:")
        print(f"  上班时间: {current['work_start_time']}")
        print(f"  下班时间: {current['work_end_time']}")
        print(f"  迟到阈值: {current['late_threshold_minutes']} 分钟")

        print("\n请输入新值 (格式 HH:MM:SS，留空保持不变):")
        start = self.input_str("上班时间: ", allow_empty=True)
        end = self.input_str("下班时间: ", allow_empty=True)
        threshold = self.input_int("迟到阈值 (分钟): ", default=None)

        if not start and not end and threshold is None:
            print("\n  没有任何更改。")
            return

        if self.config_service.set_work_hours(
            work_start_time=start or None,
            work_end_time=end or None,
            late_threshold_minutes=threshold,
        ):
            print(f"\n  ✓ 工作时间配置已更新！")
        else:
            print(f"\n  ✗ 更新失败！")

    def reset_config(self):
        self.print_header("重置配置")
        confirm = self.input_str("确认重置所有配置为默认值? (Y/N): ").upper()

        if confirm == "Y":
            confirm2 = self.input_str("再次确认，此操作不可撤销! (Y/N): ").upper()
            if confirm2 == "Y":
                if self.config_service.reset_config():
                    print(f"\n  ✓ 配置已重置为默认值！")
                else:
                    print(f"\n  ✗ 重置失败！")
            else:
                print("\n  操作已取消。")
        else:
            print("\n  操作已取消。")
