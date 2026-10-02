"""数据仓库：示例数据只有这一份，负责初始化、版本迁移与历史留档。

真实项目里这里会换成数据库访问层；当前用 JSON 文件落盘，不依赖外部组件，
就能保证「种子只维护一处、重复初始化只认第一次、口径变了自动重灌」。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules import MODULE_SPECS
from app.seed import SEED_ROWS, SEED_VERSION

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_FILE = DATA_DIR / "store.json"
ARCHIVE_DIR = DATA_DIR / "archive"


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] | None = None

    # ---- 初始化与版本迁移 ----

    def initialize(self) -> str:
        """把仓库准备到可用状态；重复初始化只认第一次。

        - 已经初始化过：直接返回，既不会多出记录，也不会冲掉任何模块的样例；
        - 落盘数据与当前种子口径同版：原样加载，保留初始化之后的全部改动；
        - 种子口径换过（SEED_VERSION 不同）：旧数据按当时那一版留档到
          archive/，再按新的一套重灌。
        """
        if self._tables is not None:
            return "already-initialized"
        if DATA_FILE.exists():
            payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if payload.get("seed_version") == SEED_VERSION:
                self._tables = payload["tables"]
                return "loaded"
            self._archive(payload)
        self._tables = {name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()}
        self._persist()
        return "seeded"

    def _archive(self, payload: dict[str, Any]) -> Path:
        """历史留档：旧版本数据整份保留，文件名带版本号与时间戳。"""
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        version = payload.get("seed_version", "unknown")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        target = ARCHIVE_DIR / f"store-v{version}-{stamp}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def _persist(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"seed_version": SEED_VERSION, "tables": self._tables}
        DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def save(self) -> None:
        """业务写操作之后落盘，重启后看到的还是同一份数据。"""
        self._persist()

    # ---- 读口径：概览与明细都从 self._tables 这同一份数据里取 ----

    @property
    def _ready_tables(self) -> dict[str, list[dict[str, Any]]]:
        if self._tables is None:
            self.initialize()
        assert self._tables is not None
        return self._tables

    def module_names(self) -> list[str]:
        return sorted(self._ready_tables)

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._ready_tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def overview(self) -> dict[str, object]:
        modules: list[dict[str, object]] = []
        for name in self.module_names():
            rows = self.rows(name)
            spec = MODULE_SPECS.get(name)
            status_counts: dict[str, int] = {}
            for row in rows:
                status = str(row.get("status", ""))
                status_counts[status] = status_counts.get(status, 0) + 1
            modules.append({
                "key": name,
                "name": spec.title if spec else name,
                "created": len(rows),
                "pending": sum(1 for row in rows if row.get("pending")),
                "abnormal": sum(1 for row in rows if row.get("abnormal")),
                "status_counts": status_counts,
            })
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"cards": cards, "modules": modules}


store = Store()
