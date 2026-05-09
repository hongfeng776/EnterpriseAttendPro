import json
import os
from typing import Any, Dict, List, Optional
from src.storage.logger import logger


class JSONStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            self._write_data([])
            logger.info(f"创建新数据文件: {self.file_path}")

    def _read_data(self) -> Any:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"读取数据文件失败 {self.file_path}: {e}")
            return []

    def _write_data(self, data: Any) -> bool:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"写入数据文件失败 {self.file_path}: {e}")
            return False

    def load_all(self) -> List[Dict]:
        data = self._read_data()
        return data if isinstance(data, list) else []

    def save_all(self, data: List[Dict]) -> bool:
        return self._write_data(data)

    def add(self, item: Dict) -> bool:
        data = self.load_all()
        data.append(item)
        result = self._write_data(data)
        if result:
            logger.debug(f"添加数据到 {self.file_path}")
        return result

    def update(self, item_id: str, updated_item: Dict, id_field: str = "id") -> bool:
        data = self.load_all()
        for i, item in enumerate(data):
            if str(item.get(id_field, "")) == str(item_id):
                data[i] = updated_item
                result = self._write_data(data)
                if result:
                    logger.debug(f"更新数据 {item_id} 在 {self.file_path}")
                return result
        return False

    def delete(self, item_id: str, id_field: str = "id") -> bool:
        data = self.load_all()
        original_count = len(data)
        data = [item for item in data if str(item.get(id_field, "")) != str(item_id)]
        if len(data) != original_count:
            result = self._write_data(data)
            if result:
                logger.debug(f"删除数据 {item_id} 从 {self.file_path}")
            return result
        return False

    def get_by_id(self, item_id: str, id_field: str = "id") -> Optional[Dict]:
        data = self.load_all()
        for item in data:
            if str(item.get(id_field, "")) == str(item_id):
                return item
        return None

    def find(self, **filters) -> List[Dict]:
        data = self.load_all()
        results = []
        for item in data:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results

    def count(self) -> int:
        return len(self.load_all())
