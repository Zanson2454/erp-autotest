"""进程内异步任务管理器。

作用：
1. 用线程池执行异步场景任务。
2. 维护任务状态流转（PENDING/RUNNING/SUCCESS/FAILED）。
3. 将任务快照持久化到本地缓存文件，支持重启后查询。
"""

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from erp_data_factory.core.models import ScenarioResult


class TaskManager:
    """异步任务生命周期管理器。"""

    def __init__(self, max_workers: int = 4, store_file: str = "testdata/cache/edf_tasks.json"):
        """初始化线程池与任务存储。

        参数：
        - max_workers: 线程池并发数。
        - store_file: 任务持久化文件路径。
        """
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="edf-task")
        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._store_file = Path(store_file)
        self._store_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_from_store()

    def submit(self, run_fn, scenario_key: str, payload: Dict[str, Any], context) -> str:
        """提交异步任务并返回 ``task_id``。"""
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "status": "PENDING",
                "scenario_key": scenario_key,
                "created_at": now,
                "updated_at": now,
                "result": None,
                "error": None,
            }

        def _job():
            self._set_status(task_id, "RUNNING")
            try:
                result: ScenarioResult = run_fn(scenario_key=scenario_key, payload=payload, context=context)
                if result.success:
                    self._set_result(task_id, "SUCCESS", result.to_dict())
                else:
                    self._set_result(task_id, "FAILED", result.to_dict())
            except Exception as e:  # pragma: no cover
                self._set_error(task_id, str(e))

        self._executor.submit(_job)
        return task_id

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        """按任务 ID 查询当前任务快照，不存在时返回 ``None``。"""
        with self._lock:
            if task_id not in self._tasks:
                self._load_from_store()
            task = self._tasks.get(task_id)
            return dict(task) if task else None

    def _set_status(self, task_id: str, status: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task["status"] = status
            task["updated_at"] = datetime.utcnow().isoformat()
            self._flush_store()

    def _set_result(self, task_id: str, status: str, result: Dict[str, Any]) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task["status"] = status
            task["result"] = result
            task["updated_at"] = datetime.utcnow().isoformat()
            self._flush_store()

    def _set_error(self, task_id: str, message: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task["status"] = "FAILED"
            task["error"] = {"message": message}
            task["updated_at"] = datetime.utcnow().isoformat()
            self._flush_store()

    def _flush_store(self) -> None:
        try:
            self._store_file.write_text(
                json.dumps(self._tasks, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:  # pragma: no cover
            return

    def _load_from_store(self) -> None:
        if not self._store_file.exists():
            return
        try:
            data = json.loads(self._store_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._tasks.update(data)
        except Exception:  # pragma: no cover
            return


_global_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取当前进程内的单例任务管理器。"""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = TaskManager()
    return _global_task_manager
