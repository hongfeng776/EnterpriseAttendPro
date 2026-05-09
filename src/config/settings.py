import os
from datetime import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

EMPLOYEE_DATA_FILE = os.path.join(DATA_DIR, "employees.json")
ATTENDANCE_DATA_FILE = os.path.join(DATA_DIR, "attendance.json")
LEAVE_DATA_FILE = os.path.join(DATA_DIR, "leave.json")
SALARY_DATA_FILE = os.path.join(DATA_DIR, "salary.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

WORK_START_TIME = time(9, 0, 0)
WORK_END_TIME = time(18, 0, 0)
LATE_THRESHOLD_MINUTES = 30

DEPARTMENTS = ["技术部", "市场部", "人事部", "财务部", "销售部", "行政部"]
POSITIONS = ["员工", "主管", "经理", "总监", "总经理"]
LEAVE_TYPES = ["年假", "病假", "事假", "婚假", "产假", "丧假"]
LEAVE_STATUS = ["待审批", "已批准", "已拒绝"]

DEFAULT_SALARY_BASE = 5000
OVERTIME_RATE = 1.5
LATE_DEDUCTION = 50
EARLY_LEAVE_DEDUCTION = 50
ABSENCE_DEDUCTION = 200

for directory in [DATA_DIR, LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
