"""开关电源业务规则：状态流转、字段校验与筛选口径都收在这里。

字段名与状态取值统一从 app.seed 取用，不再自己维护一份。
"""
from __future__ import annotations

from typing import Any

from app.seed import MODULE_FIELDS, STATUS_ORDER, STATUS_ABNORMAL, STATUS_ATTENTION, STATUS_DISABLED, derive_flags
from app.store import store

MODULE = "rectifier"
LABEL = "开关电源"
NOUN = "开关电源"
FIELDS = MODULE_FIELDS[MODULE]
KEYWORD_FIELD = FIELDS[0]
REQUIRED_FIELDS = FIELDS[:3]
ACTION_RULES = {"记录缺失": STATUS_ATTENTION, "记录异常": STATUS_ABNORMAL, "安排更换": STATUS_DISABLED}


class RectifierService:
    def list_entries(
        self,
        *,
        keyword: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict[str, Any]], int, dict[str, int]]:
        rows = store.rows(MODULE)
        if keyword:
            rows = [row for row in rows if keyword in str(row.get(KEYWORD_FIELD, ""))]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        summary = store.summarize(rows)
        total = len(rows)
        start = max(page - 1, 0) * size
        return rows[start:start + size], total, summary

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        return store.find(MODULE, entry_id)

    def create_entry(self, values: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        missing = [field for field in REQUIRED_FIELDS if not str(values.get(field) or "").strip()]
        if missing:
            return None, missing
        rows = store.rows(MODULE)
        entry = {"id": max((int(row.get("id", 0)) for row in rows), default=0) + 1}
        entry.update({field: values.get(field) for field in REQUIRED_FIELDS})
        entry["status"] = STATUS_ORDER[0]
        entry.update(derive_flags(entry["status"]))
        rows.append(entry)
        store.save()
        return entry, []

    def run_action(self, entry_id: int, action: str) -> tuple[dict[str, Any] | None, str]:
        entry = store.find(MODULE, entry_id)
        if entry is None:
            return None, f"{NOUN} {entry_id} 不存在或已归档"
        if action not in ACTION_RULES:
            return None, f"动作「{action}」不属于{LABEL}可执行范围"
        target = ACTION_RULES[action]
        if target not in STATUS_ORDER:
            return None, f"目标状态「{target}」不在允许的状态序列里"
        entry["status"] = target
        entry.update(derive_flags(target))
        store.save()
        return entry, f"{NOUN}已{action}"
