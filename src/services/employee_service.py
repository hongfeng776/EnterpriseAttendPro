from typing import List, Optional
from datetime import datetime
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
