"""运行配置：端口、跨域、运行环境与数据落盘位置。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "通信基站运维管理平台"
    env: str = "local"
    port: int = 8000
    allowed_origins: list[str] = field(
        default_factory=lambda: [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )
    page_size_default: int = 20
    page_size_max: int = 200
    # 数据落盘位置：默认 backend/data/store.json，可用 STORE_STATE_PATH 指到别处。
    state_path: str = field(
        default_factory=lambda: os.environ.get(
            "STORE_STATE_PATH",
            str(Path(__file__).resolve().parent.parent / "data" / "store.json"),
        )
    )


settings = Settings()
