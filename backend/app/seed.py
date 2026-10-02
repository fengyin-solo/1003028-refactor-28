"""示例数据：按模块登记表生成，全平台只有这一份种子口径。

每个模块固定三条样例，状态取状态序列的前三档：两条待处理（其中一条异常）、
一条已办结。概览卡片与列表都数自这同一份数据，数字天然对得上。

口径要调整时，改 MODULE_SPECS 或本文件的取值规则，并把 SEED_VERSION 加一：
已经初始化过的环境会在下次启动时把旧数据按当时那一版留档，再按新口径重灌。
"""
from __future__ import annotations

from typing import Any

from app.modules import MODULE_SPECS

SEED_VERSION = 1

# 样例取值的统一规则：编号列写模块编号、日期/时间列写固定日期、
# 数量列写整数、金额列写小数，其余文本列写「<模块名>样例N」。
_DATE_MARKERS = ("日期", "时间")
_INT_MARKERS = ("数量",)
_FLOAT_MARKERS = ("金额",)


def _sample_value(module_title: str, field_name: str, code: str, index: int) -> Any:
    if field_name.endswith("编号"):
        return code
    if any(marker in field_name for marker in _DATE_MARKERS):
        return f"2026-09-0{index}"
    if any(marker in field_name for marker in _INT_MARKERS):
        return index * 10
    if any(marker in field_name for marker in _FLOAT_MARKERS):
        return index * 12.5
    return f"{module_title}样例{index}"


def build_seed_rows() -> dict[str, list[dict[str, Any]]]:
    """按登记表生成各模块的初始样例；字段名与状态取值与登记表完全一致。"""
    tables: dict[str, list[dict[str, Any]]] = {}
    for key, spec in MODULE_SPECS.items():
        prefix = key.upper()[:4]
        rows: list[dict[str, Any]] = []
        for index in (1, 2, 3):
            code = f"{prefix}-{index:04d}"
            row: dict[str, Any] = {
                "id": index,
                "status": spec.statuses[index - 1],
                "pending": index < 3,
                "abnormal": index == 2,
            }
            for field_name in spec.fields:
                row[field_name] = _sample_value(spec.title, field_name, code, index)
            rows.append(row)
        tables[key] = rows
    return tables


SEED_ROWS = build_seed_rows()
