"""数据仓库：全模块共用一份种子口径，落盘保存，按版本重灌。

- 首次启动：按 seed.py 的口径初始化全部模块，并记录种子版本；
- 再次启动且版本一致：直接沿用既有数据——重复初始化只认第一次，
  不会多出记录，也不会把某个模块的样例冲掉；
- 种子版本升级：先把当前数据按当时那一版整体留档到 archive/，再按新口径重灌。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from app import seed
from app.config import settings


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Store:
    def __init__(self, state_path: Path | None = None) -> None:
        self._state_path = state_path or Path(settings.state_path)
        self._tables: dict[str, list[dict[str, Any]]] = {}
        self._meta: dict[str, Any] = {}
        self.initialize()

    @property
    def seed_version(self) -> str:
        return str(self._meta.get("seed_version", seed.SEED_VERSION))

    # ---------- 初始化与版本迁移 ----------

    def initialize(self) -> None:
        """装载既有数据或按种子口径初始化；重复调用只认第一次。"""
        state = self._read_state()
        if state is None:
            self._tables = seed.build_seed_rows()
            self._meta = {"seed_version": seed.SEED_VERSION, "initialized_at": _now()}
            self._persist()
            return
        self._meta = state["meta"]
        self._tables = state["tables"]
        if self._meta.get("seed_version") != seed.SEED_VERSION:
            # 种子口径换过：历史留档按当时那一版保留，再按新的一套重灌。
            self._archive()
            self._tables = seed.build_seed_rows()
            self._meta = {"seed_version": seed.SEED_VERSION, "initialized_at": _now()}
            self._persist()
            return
        self._top_up_missing_modules()

    def _top_up_missing_modules(self) -> None:
        """只补齐缺失的模块；已有模块一行不动，样例不会被冲掉。"""
        missing = {
            module: rows
            for module, rows in seed.build_seed_rows().items()
            if module not in self._tables
        }
        if missing:
            self._tables.update(missing)
            self._persist()

    def _read_state(self) -> dict[str, Any] | None:
        if not self._state_path.exists():
            return None
        try:
            state = json.loads(self._state_path.read_text(encoding="utf-8"))
            if isinstance(state, dict) and isinstance(state.get("tables"), dict):
                return {"meta": dict(state.get("meta") or {}), "tables": state["tables"]}
        except (OSError, json.JSONDecodeError):
            pass
        # 状态文件损坏：留档后当作未初始化，交给上层按种子口径重灌。
        self._quarantine()
        return None

    def _archive(self) -> Path:
        """把当前状态文件整体留档，文件名带当时的种子版本。"""
        old_version = str(self._meta.get("seed_version", "unknown")).replace("/", "-")
        return self._copy_to_archive(f"store_v{old_version}_{datetime.now():%Y%m%d-%H%M%S}.json")

    def _quarantine(self) -> Path:
        return self._copy_to_archive(f"store_corrupt_{datetime.now():%Y%m%d-%H%M%S}.json")

    def _copy_to_archive(self, filename: str) -> Path:
        archive_dir = self._state_path.parent / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        target = archive_dir / filename
        shutil.copy2(self._state_path, target)
        return target

    def _persist(self) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"meta": self._meta, "tables": self._tables}
        tmp_path = self._state_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(self._state_path)

    def save(self) -> None:
        """业务动作改完数据后落盘，保证重启后环境还是初始化过的样子。"""
        self._persist()

    # ---------- 读取与统计 ----------

    def module_names(self) -> list[str]:
        return sorted(self._tables)

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def summarize(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        """按统一口径汇总一组记录：列表统计与概览看板都用它。"""
        pending = 0
        abnormal = 0
        for row in rows:
            flags = seed.derive_flags(str(row.get("status", "")))
            pending += flags["pending"]
            abnormal += flags["abnormal"]
        return {"total": len(rows), "pending": pending, "abnormal": abnormal}

    def overview(self) -> dict[str, object]:
        modules: list[dict[str, object]] = []
        for name in self.module_names():
            summary = self.summarize(self.rows(name))
            modules.append({
                "name": name,
                "label": seed.MODULE_LABELS.get(name, name),
                **summary,
            })
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "记录总数", "value": sum(int(item["total"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"seed_version": self.seed_version, "cards": cards, "modules": modules}


store = Store()
