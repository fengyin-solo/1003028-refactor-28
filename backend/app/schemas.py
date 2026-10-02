"""接口出入参模型：列表分页、动作结果与登记载荷。

各模块的明细结构不再单独建模：字段名统一取 seed.py 里的中文列名，
接口直接以 dict 出入参，避免同一批字段维护两套写法。
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    size: int = 20
    # 当前过滤条件下的汇总（待处理/异常），与列表内容同一份口径。
    summary: dict[str, int] | None = None


class ActionResult(BaseModel):
    ok: bool
    message: str
    entry: dict[str, Any] | None = None


class EntryPayload(BaseModel):
    """登记或修改一条业务记录时提交的字段集合。"""

    values: dict[str, Any] = Field(default_factory=dict)
    remark: str | None = None
