"""空调管理业务规则：状态流转、字段校验与筛选口径都收在这里。"""
from __future__ import annotations

from app.modules import MODULE_SPECS
from app.services.base import ModuleService

MODULE = "ac"
SPEC = MODULE_SPECS[MODULE]


class AcService(ModuleService):
    """字段、状态与动作口径取自模块登记表，不在本文件另写一份。"""

    spec = SPEC
