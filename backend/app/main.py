"""通信基站运维管理平台 后端服务入口。

启动：uvicorn app.main:app --host 127.0.0.1 --port 8000
健康检查：GET /api/health
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.modules import MODULE_SPECS
from app.routers import ROUTERS
from app.seed import SEED_VERSION
from app.store import store

app = FastAPI(title="通信基站运维管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in ROUTERS:
    app.include_router(module.router)

# 启动时初始化数据仓库：重复初始化只认第一次；种子口径换过会自动归档旧版再重灌。
STORE_INIT_RESULT = store.initialize()


@app.get("/api/health")
def health() -> dict[str, object]:
    """健康检查：确认服务已经监听、示例数据已经就绪。"""
    return {
        "ok": True,
        "app": settings.app_name,
        "modules": len(store.module_names()),
        "seed_version": SEED_VERSION,
        "store": STORE_INIT_RESULT,
    }


@app.get("/api/modules")
def modules() -> list[dict[str, object]]:
    """模块登记表：字段名、状态取值与可执行动作，前端页面与种子数据共用这一份。"""
    return [
        {
            "key": spec.key,
            "title": spec.title,
            "noun": spec.noun,
            "fields": list(spec.fields),
            "statuses": list(spec.statuses),
            "actions": list(spec.actions),
            "stats": [{"label": card.label, "status": card.status} for card in spec.stats],
        }
        for spec in MODULE_SPECS.values()
    ]


@app.get("/api/overview")
def overview() -> dict[str, object]:
    """运营概览：与各模块明细数自同一份数据，先汇总待处理量再看异常。"""
    return store.overview()
