"""数据仓库的初始化与版本迁移行为：重复初始化、版本重灌、历史留档。"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import seed
from app.store import Store


class StoreLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.state_path = Path(self._tmp.name) / "store.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_first_init_seeds_all_modules_with_shared_spec(self) -> None:
        store = Store(self.state_path)
        self.assertEqual(store.seed_version, seed.SEED_VERSION)
        self.assertTrue(self.state_path.exists())
        for module, fields in seed.MODULE_FIELDS.items():
            rows = store.rows(module)
            self.assertEqual(len(rows), len(seed.SAMPLE_STATUSES))
            for row in rows:
                # 字段名按统一的中文列名，状态取值来自统一集合
                for field in fields:
                    self.assertIn(field, row)
                self.assertIn(row["status"], seed.STATUS_ORDER)
                # 看板标记与状态按统一规则推导
                flags = seed.derive_flags(row["status"])
                self.assertEqual(row["pending"], flags["pending"])
                self.assertEqual(row["abnormal"], flags["abnormal"])

    def test_repeated_init_is_noop(self) -> None:
        store = Store(self.state_path)
        store.rows("site")[0]["基站名称"] = "手工改过的名字"
        store.save()
        snapshot = self.state_path.read_text(encoding="utf-8")

        again = Store(self.state_path)  # 重复初始化只认第一次
        self.assertEqual(again.rows("site")[0]["基站名称"], "手工改过的名字")  # 样例不被冲掉
        self.assertEqual(len(again.rows("site")), len(seed.SAMPLE_STATUSES))  # 不多出记录
        self.assertEqual(self.state_path.read_text(encoding="utf-8"), snapshot)  # 文件未被改写

    def test_missing_module_topped_up_without_touching_others(self) -> None:
        store = Store(self.state_path)
        store.rows("site")[0]["基站名称"] = "手工改过的名字"
        store.save()
        # 模拟某个模块的数据丢失
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        del state["tables"]["tower"]
        self.state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        again = Store(self.state_path)
        self.assertEqual(len(again.rows("tower")), len(seed.SAMPLE_STATUSES))  # 缺失模块补齐
        self.assertEqual(again.rows("site")[0]["基站名称"], "手工改过的名字")  # 其他模块不动

    def test_seed_version_bump_archives_then_reseeds(self) -> None:
        store = Store(self.state_path)
        store.rows("site")[0]["基站名称"] = "旧版数据"
        store.save()

        original = seed.SEED_VERSION
        seed.SEED_VERSION = original + "-next"  # 种子口径换过
        try:
            migrated = Store(self.state_path)
        finally:
            seed.SEED_VERSION = original

        self.assertEqual(migrated.seed_version, original + "-next")
        # 按新的一套重灌：旧改动不保留
        self.assertEqual(migrated.rows("site")[0]["基站名称"], "基站台账样例1")
        # 历史留档按当时那一版保留
        archives = list((self.state_path.parent / "archive").glob("*.json"))
        self.assertEqual(len(archives), 1)
        archived = json.loads(archives[0].read_text(encoding="utf-8"))
        self.assertEqual(archived["meta"]["seed_version"], original)
        self.assertEqual(archived["tables"]["site"][0]["基站名称"], "旧版数据")

    def test_overview_matches_list_rows(self) -> None:
        store = Store(self.state_path)
        overview = store.overview()
        modules = {item["name"]: item for item in overview["modules"]}
        for name in store.module_names():
            summary = store.summarize(store.rows(name))
            self.assertEqual(modules[name]["total"], summary["total"])
            self.assertEqual(modules[name]["pending"], summary["pending"])
            self.assertEqual(modules[name]["abnormal"], summary["abnormal"])
        cards = {card["label"]: card["value"] for card in overview["cards"]}
        self.assertEqual(cards["记录总数"], sum(item["total"] for item in modules.values()))
        self.assertEqual(cards["待处理"], sum(item["pending"] for item in modules.values()))
        self.assertEqual(cards["异常量"], sum(item["abnormal"] for item in modules.values()))


if __name__ == "__main__":
    unittest.main()
