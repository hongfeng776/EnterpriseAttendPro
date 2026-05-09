from typing import List, Optional, Dict, Tuple
from datetime import datetime
import os
import csv
from src.models.employee import Employee
from src.storage.json_storage import JSONStorage
from src.storage.logger import logger
from src.config.settings import EMPLOYEE_DATA_FILE, DEFAULT_SALARY_BASE


class EmployeeService:
    def __init__(self):
        self.storage = JSONStorage(EMPLOYEE_DATA_FILE)
        self._init_employee_counter()

    def _init_employee_counter(self):
        pass

    def generate_employee_no(self) -> str:
        employees = self.storage.load_all()
        if not employees:
            return "EMP001"
        max_no = 0
        for emp in employees:
            emp_no = emp.get("employee_no", "")
            if emp_no.startswith("EMP"):
                try:
                    num = int(emp_no[3:])
                    if num > max_no:
                        max_no = num
                except ValueError:
                    continue
        new_no = max_no + 1
        return f"EMP{new_no:03d}"

    def add_employee(
        self,
        name: str,
        gender: str,
        department: str,
        position: str,
        phone: str,
        email: str,
        join_date: str,
        base_salary: float = None,
    ) -> Optional[Employee]:
        try:
            employee = Employee(
                id=Employee.generate_id(),
                employee_no=self.generate_employee_no(),
                name=name,
                gender=gender,
                department=department,
                position=position,
                phone=phone,
                email=email,
                join_date=join_date,
                base_salary=base_salary if base_salary is not None else DEFAULT_SALARY_BASE,
                status="在职",
            )
            if self.storage.add(employee.to_dict()):
                logger.info(f"新增员工: {employee.name} ({employee.employee_no})")
                return employee
            return None
        except Exception as e:
            logger.error(f"添加员工失败: {e}")
            return None

    def get_all_employees(self) -> List[Employee]:
        data = self.storage.load_all()
        return [Employee.from_dict(item) for item in data]

    def get_employee_by_id(self, emp_id: str) -> Optional[Employee]:
        data = self.storage.get_by_id(emp_id)
        return Employee.from_dict(data) if data else None

    def get_employee_by_no(self, emp_no: str) -> Optional[Employee]:
        employees = self.storage.find(employee_no=emp_no)
        return Employee.from_dict(employees[0]) if employees else None

    def search_employees(self, keyword: str) -> List[Employee]:
        all_emps = self.get_all_employees()
        keyword = keyword.lower()
        results = []
        for emp in all_emps:
            if (
                keyword in emp.name.lower()
                or keyword in emp.employee_no.lower()
                or keyword in emp.department.lower()
                or keyword in emp.phone
            ):
                results.append(emp)
        return results

    def update_employee(
        self,
        emp_id: str,
        name: str = None,
        gender: str = None,
        department: str = None,
        position: str = None,
        phone: str = None,
        email: str = None,
        join_date: str = None,
        base_salary: float = None,
        status: str = None,
    ) -> bool:
        employee = self.get_employee_by_id(emp_id)
        if not employee:
            logger.warning(f"未找到员工 ID: {emp_id}")
            return False

        if name is not None:
            employee.name = name
        if gender is not None:
            employee.gender = gender
        if department is not None:
            employee.department = department
        if position is not None:
            employee.position = position
        if phone is not None:
            employee.phone = phone
        if email is not None:
            employee.email = email
        if join_date is not None:
            employee.join_date = join_date
        if base_salary is not None:
            employee.base_salary = base_salary
        if status is not None:
            employee.status = status

        result = self.storage.update(emp_id, employee.to_dict())
        if result:
            logger.info(f"更新员工信息: {employee.name}")
        return result

    def delete_employee(self, emp_id: str) -> bool:
        employee = self.get_employee_by_id(emp_id)
        if employee:
            result = self.storage.delete(emp_id)
            if result:
                logger.info(f"删除员工: {employee.name} ({employee.employee_no})")
            return result
        return False

    def get_employees_by_department(self, department: str) -> List[Employee]:
        employees = self.storage.find(department=department)
        return [Employee.from_dict(item) for item in employees]

    def count_employees(self) -> int:
        return self.storage.count()

    def count_employees_by_status(self, status: str) -> int:
        return len(self.storage.find(status=status))

    def filter_employees(
        self,
        department: str = None,
        employee_no: str = None,
        name: str = None,
        status: str = None,
        position: str = None,
    ) -> List[Employee]:
        all_emps = self.get_all_employees()
        results = []

        for emp in all_emps:
            match = True

            if department and department != emp.department:
                match = False
            if employee_no and employee_no.lower() not in emp.employee_no.lower():
                match = False
            if name and name.lower() not in emp.name.lower():
                match = False
            if status and status != emp.status:
                match = False
            if position and position != emp.position:
                match = False

            if match:
                results.append(emp)

        return results

    def batch_import_from_csv(self, file_path: str, skip_header: bool = True) -> Tuple[int, int, List[str]]:
        if not os.path.exists(file_path):
            logger.error(f"CSV文件不存在: {file_path}")
            return (0, 0, [f"文件不存在: {file_path}"])

        success_count = 0
        fail_count = 0
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                row_number = 0

                for row in reader:
                    row_number += 1

                    if skip_header and row_number == 1:
                        continue

                    if not row or len(row) < 6:
                        errors.append(f"第{row_number}行: 数据格式错误，字段不足")
                        fail_count += 1
                        continue

                    try:
                        name = row[0].strip()
                        gender = row[1].strip()
                        department = row[2].strip()
                        position = row[3].strip()
                        phone = row[4].strip()
                        email = row[5].strip() if len(row) > 5 else ""
                        join_date = row[6].strip() if len(row) > 6 else datetime.now().strftime("%Y-%m-%d")
                        base_salary = float(row[7].strip()) if len(row) > 7 and row[7].strip() else DEFAULT_SALARY_BASE

                        if not name or not gender or not department or not position or not phone:
                            errors.append(f"第{row_number}行: 必填字段为空")
                            fail_count += 1
                            continue

                        employee = self.add_employee(
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
                            success_count += 1
                        else:
                            errors.append(f"第{row_number}行: 保存失败")
                            fail_count += 1

                    except ValueError as e:
                        errors.append(f"第{row_number}行: 数据格式错误 - {str(e)}")
                        fail_count += 1
                    except Exception as e:
                        errors.append(f"第{row_number}行: 未知错误 - {str(e)}")
                        fail_count += 1

            logger.info(f"CSV导入完成: 成功{success_count}条, 失败{fail_count}条")
            return (success_count, fail_count, errors)

        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            return (0, 0, [f"读取文件失败: {str(e)}"])

    def batch_import_from_txt(self, file_path: str, delimiter: str = ",") -> Tuple[int, int, List[str]]:
        if not os.path.exists(file_path):
            logger.error(f"TXT文件不存在: {file_path}")
            return (0, 0, [f"文件不存在: {file_path}"])

        success_count = 0
        fail_count = 0
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            row_number = 0
            for line in lines:
                row_number += 1
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = [p.strip() for p in line.split(delimiter)]

                if len(parts) < 6:
                    errors.append(f"第{row_number}行: 数据格式错误，字段不足")
                    fail_count += 1
                    continue

                try:
                    name = parts[0]
                    gender = parts[1]
                    department = parts[2]
                    position = parts[3]
                    phone = parts[4]
                    email = parts[5] if len(parts) > 5 else ""
                    join_date = parts[6] if len(parts) > 6 else datetime.now().strftime("%Y-%m-%d")
                    base_salary = float(parts[7]) if len(parts) > 7 and parts[7] else DEFAULT_SALARY_BASE

                    if not name or not gender or not department or not position or not phone:
                        errors.append(f"第{row_number}行: 必填字段为空")
                        fail_count += 1
                        continue

                    employee = self.add_employee(
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
                        success_count += 1
                    else:
                        errors.append(f"第{row_number}行: 保存失败")
                        fail_count += 1

                except ValueError as e:
                    errors.append(f"第{row_number}行: 数据格式错误 - {str(e)}")
                    fail_count += 1
                except Exception as e:
                    errors.append(f"第{row_number}行: 未知错误 - {str(e)}")
                    fail_count += 1

            logger.info(f"TXT导入完成: 成功{success_count}条, 失败{fail_count}条")
            return (success_count, fail_count, errors)

        except Exception as e:
            logger.error(f"读取TXT文件失败: {e}")
            return (0, 0, [f"读取文件失败: {str(e)}"])

    def export_to_csv(self, file_path: str, employees: List[Employee] = None) -> bool:
        if employees is None:
            employees = self.get_all_employees()

        try:
            with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "员工编号", "姓名", "性别", "部门", "职位",
                    "电话", "邮箱", "入职日期", "基本薪资", "状态", "创建时间"
                ])

                for emp in employees:
                    writer.writerow([
                        emp.employee_no,
                        emp.name,
                        emp.gender,
                        emp.department,
                        emp.position,
                        emp.phone,
                        emp.email,
                        emp.join_date,
                        emp.base_salary,
                        emp.status,
                        emp.created_at,
                    ])

            logger.info(f"CSV导出成功: {file_path}, 共{len(employees)}条记录")
            return True

        except Exception as e:
            logger.error(f"导出CSV文件失败: {e}")
            return False

    def export_to_txt(self, file_path: str, employees: List[Employee] = None, delimiter: str = ",") -> bool:
        if employees is None:
            employees = self.get_all_employees()

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# 员工编号,姓名,性别,部门,职位,电话,邮箱,入职日期,基本薪资,状态,创建时间\n")

                for emp in employees:
                    line = delimiter.join([
                        emp.employee_no,
                        emp.name,
                        emp.gender,
                        emp.department,
                        emp.position,
                        emp.phone,
                        emp.email,
                        emp.join_date,
                        str(emp.base_salary),
                        emp.status,
                        emp.created_at,
                    ])
                    f.write(line + "\n")

            logger.info(f"TXT导出成功: {file_path}, 共{len(employees)}条记录")
            return True

        except Exception as e:
            logger.error(f"导出TXT文件失败: {e}")
            return False

    def get_import_template(self) -> str:
        return (
            "员工信息导入格式说明:\n"
            "字段顺序: 姓名,性别,部门,职位,电话,邮箱,入职日期,基本薪资\n"
            "分隔符: 逗号 (,)\n"
            "示例:\n"
            "张三,男,技术部,开发工程师,13800138001,zhangsan@example.com,2024-01-01,8000\n"
            "李四,女,市场部,销售经理,13800138002,lisi@example.com,2024-02-15,10000\n"
            "\n"
            "必填字段: 姓名、性别、部门、职位、电话\n"
            "可选字段: 邮箱、入职日期(默认今天)、基本薪资(默认5000)"
        )
