from typing import Dict, Any, Optional
from datetime import time
import json
import os
from src.storage.logger import logger
from src.config.settings import (
    CONFIG_FILE,
    DEPARTMENTS,
    POSITIONS,
    LEAVE_TYPES,
    DEFAULT_SALARY_BASE,
    OVERTIME_RATE,
    LATE_DEDUCTION,
    EARLY_LEAVE_DEDUCTION,
    ABSENCE_DEDUCTION,
    LATE_THRESHOLD_MINUTES,
)


class SystemConfigService:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self._ensure_config_file()

    def _ensure_config_file(self):
        if not os.path.exists(self.config_file):
            default_config = self._get_default_config()
            self._save_config(default_config)
            logger.info("创建默认系统配置文件")

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "system": {
                "name": "企业级员工考勤管理系统",
                "version": "1.0.0",
                "language": "zh-CN",
            },
            "work_hours": {
                "work_start_time": "09:00:00",
                "work_end_time": "18:00:00",
                "late_threshold_minutes": LATE_THRESHOLD_MINUTES,
            },
            "salary": {
                "default_base_salary": DEFAULT_SALARY_BASE,
                "overtime_rate": OVERTIME_RATE,
                "late_deduction": LATE_DEDUCTION,
                "early_leave_deduction": EARLY_LEAVE_DEDUCTION,
                "absence_deduction": ABSENCE_DEDUCTION,
            },
            "departments": DEPARTMENTS.copy(),
            "positions": POSITIONS.copy(),
            "leave_types": LEAVE_TYPES.copy(),
            "notifications": {
                "enable_reminder": True,
                "reminder_time": "08:45",
            },
        }

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_default_config()

    def _save_config(self, config: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info("系统配置已保存")
            return True
        except IOError as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def get_all_config(self) -> Dict[str, Any]:
        return self._load_config()

    def get_config(self, section: str, key: str = None) -> Any:
        config = self._load_config()
        section_data = config.get(section, {})
        if key is None:
            return section_data
        return section_data.get(key)

    def set_config(self, section: str, key: str, value: Any) -> bool:
        config = self._load_config()
        if section not in config:
            config[section] = {}
        config[section][key] = value
        return self._save_config(config)

    def update_section(self, section: str, values: Dict[str, Any]) -> bool:
        config = self._load_config()
        if section not in config:
            config[section] = {}
        config[section].update(values)
        return self._save_config(config)

    def get_departments(self) -> list:
        return self.get_config("departments") or DEPARTMENTS.copy()

    def add_department(self, dept_name: str) -> bool:
        depts = self.get_departments()
        if dept_name in depts:
            logger.warning(f"部门已存在: {dept_name}")
            return False
        depts.append(dept_name)
        return self.update_section("departments", depts)

    def remove_department(self, dept_name: str) -> bool:
        depts = self.get_departments()
        if dept_name not in depts:
            logger.warning(f"部门不存在: {dept_name}")
            return False
        depts.remove(dept_name)
        return self.update_section("departments", depts)

    def get_positions(self) -> list:
        return self.get_config("positions") or POSITIONS.copy()

    def add_position(self, position_name: str) -> bool:
        positions = self.get_positions()
        if position_name in positions:
            logger.warning(f"职位已存在: {position_name}")
            return False
        positions.append(position_name)
        return self.update_section("positions", positions)

    def remove_position(self, position_name: str) -> bool:
        positions = self.get_positions()
        if position_name not in positions:
            logger.warning(f"职位不存在: {position_name}")
            return False
        positions.remove(position_name)
        return self.update_section("positions", positions)

    def get_leave_types(self) -> list:
        return self.get_config("leave_types") or LEAVE_TYPES.copy()

    def add_leave_type(self, leave_type: str) -> bool:
        types = self.get_leave_types()
        if leave_type in types:
            logger.warning(f"请假类型已存在: {leave_type}")
            return False
        types.append(leave_type)
        return self.update_section("leave_types", types)

    def remove_leave_type(self, leave_type: str) -> bool:
        types = self.get_leave_types()
        if leave_type not in types:
            logger.warning(f"请假类型不存在: {leave_type}")
            return False
        types.remove(leave_type)
        return self.update_section("leave_types", types)

    def get_salary_config(self) -> Dict[str, Any]:
        return self.get_config("salary")

    def set_salary_config(
        self,
        default_base_salary: float = None,
        overtime_rate: float = None,
        late_deduction: float = None,
        early_leave_deduction: float = None,
        absence_deduction: float = None,
    ) -> bool:
        current = self.get_salary_config()
        updates = {}
        if default_base_salary is not None:
            updates["default_base_salary"] = default_base_salary
        if overtime_rate is not None:
            updates["overtime_rate"] = overtime_rate
        if late_deduction is not None:
            updates["late_deduction"] = late_deduction
        if early_leave_deduction is not None:
            updates["early_leave_deduction"] = early_leave_deduction
        if absence_deduction is not None:
            updates["absence_deduction"] = absence_deduction

        current.update(updates)
        return self.update_section("salary", current)

    def get_work_hours(self) -> Dict[str, Any]:
        return self.get_config("work_hours")

    def set_work_hours(
        self,
        work_start_time: str = None,
        work_end_time: str = None,
        late_threshold_minutes: int = None,
    ) -> bool:
        current = self.get_work_hours()
        updates = {}
        if work_start_time is not None:
            updates["work_start_time"] = work_start_time
        if work_end_time is not None:
            updates["work_end_time"] = work_end_time
        if late_threshold_minutes is not None:
            updates["late_threshold_minutes"] = late_threshold_minutes

        current.update(updates)
        return self.update_section("work_hours", current)

    def reset_config(self) -> bool:
        default_config = self._get_default_config()
        return self._save_config(default_config)
