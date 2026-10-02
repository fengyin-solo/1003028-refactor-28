"""通用业务规则：列表筛选、登记与状态流转，全部按模块登记表执行。

各模块的差异只来自 ModuleSpec，不在代码里另写一份字段名或状态取值。
"""
from __future__ import annotations

from typing import Any

from app.modules import ModuleSpec
from app.store import store


class ModuleService:
    """各模块共用的业务规则；子类只需指定 spec。"""

    spec: ModuleSpec

    def list_entries(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        rows = store.rows(self.spec.key)
        if keyword:
            rows = [row for row in rows if keyword in str(row.get(self.spec.keyword_field, ""))]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        total = len(rows)
        start = max(page - 1, 0) * size
        return rows[start:start + size], total

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        return store.find(self.spec.key, entry_id)

    def create_entry(self, values: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        missing = [field for field in self.spec.required_fields if not str(values.get(field) or "").strip()]
        if missing:
            return None, missing
        rows = store.rows(self.spec.key)
        entry = {"id": max((int(row.get("id", 0)) for row in rows), default=0) + 1}
        entry.update({field: values.get(field) for field in self.spec.required_fields})
        entry["status"] = self.spec.statuses[0]
        entry["pending"] = True
        entry["abnormal"] = False
        rows.append(entry)
        store.save()
        return entry, []

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str]:
        entry = store.find(self.spec.key, entry_id)
        if entry is None:
            return None, f"{self.spec.noun} {entry_id} 不存在或已归档"
        if action not in self.spec.actions:
            return None, f"动作「{action}」不属于{self.spec.title}可执行范围"
        target = self.spec.actions[action]
        if target not in self.spec.statuses:
            return None, f"目标状态「{target}」不在允许的状态序列里"
        entry["status"] = target
        entry["pending"] = target != self.spec.statuses[-1]
        entry["abnormal"] = action in self.spec.negative_actions
        store.save()
        return entry, f"{self.spec.noun}已{action}"
