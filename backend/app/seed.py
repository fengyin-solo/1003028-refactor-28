"""示例数据与初始态的唯一出处。

全平台共用这一份口径：
- 字段名统一用中文列名（前端表格、接口出参、必填校验都按列名取值）；
- 状态取值全模块共用 STATUS_ORDER 这一套，不再每个模块各写各的；
- pending / abnormal 由状态按 derive_flags 统一推导，概览和明细自然对得上。

调整种子口径（字段、状态取值、样例行）时递增 SEED_VERSION：
已初始化的环境会在下次启动时先把当时那一版整体留档，再按新口径重灌。
"""
from __future__ import annotations

from typing import Any

# 种子口径版本：字段、状态取值或样例行有调整就递增。
SEED_VERSION = "2026.10"

# 统一状态取值：所有模块共用同一条生命周期。
STATUS_NORMAL = "正常"
STATUS_ATTENTION = "关注"
STATUS_ABNORMAL = "异常"
STATUS_DISABLED = "停用"
STATUS_ORDER = [STATUS_NORMAL, STATUS_ATTENTION, STATUS_ABNORMAL, STATUS_DISABLED]


def derive_flags(status: str) -> dict[str, bool]:
    """看板标记的统一口径：关注/异常计待处理，异常状态计异常量。"""
    return {
        "pending": status in (STATUS_ATTENTION, STATUS_ABNORMAL),
        "abnormal": status == STATUS_ABNORMAL,
    }


# 模块中文名：概览看板、接口标签与样例文本共用。
MODULE_LABELS: dict[str, str] = {
    "site": "基站台账",
    "tower": "铁塔管理",
    "power": "动力配套",
    "battery": "蓄电池组",
    "genset": "发电机组",
    "rectifier": "开关电源",
    "ac": "空调管理",
    "antenna": "天馈系统",
    "transmission": "传输设备",
    "feeder": "馈线巡检",
    "lightningprot": "防雷接地",
    "firealarm": "消防设施",
    "dooraccess": "门禁管理",
    "patrol": "巡检作业",
    "fuel": "油料管理",
    "rental": "场租合同",
    "electricbill": "电费管理",
    "demolition": "拆站管理",
    "emergency": "应急通信",
    "energyeff": "节能改造",
}

# 各模块的字段名（中文列名）：种子、接口、前端表格都按这一份取用。
MODULE_FIELDS: dict[str, list[str]] = {
    "site": ["基站编号", "基站名称", "基站类型", "所属区县", "经纬度坐标", "铁塔高度", "入网日期", "基站状态"],
    "tower": ["铁塔编号", "铁塔类型", "设计高度", "平台数量", "所属站点", "建成年份", "上次检测", "铁塔状态"],
    "power": ["设备编号", "设备类型", "额定功率", "所属站点", "投用日期", "上次检修", "下次检修日", "设备状态"],
    "battery": ["电池组编号", "电池类型", "额定容量", "所属站点", "放电时长", "内阻值", "投用日期", "电池状态"],
    "genset": ["机组编号", "机组型号", "额定功率", "所属站点", "上次试机", "油量储备", "启动状态", "机组状态"],
    "rectifier": ["电源编号", "额定功率", "所属站点", "整流模块数", "负载率", "输出电压", "模块故障", "电源状态"],
    "ac": ["空调编号", "空调类型", "制冷量", "所属站点", "运行电流", "设定温度", "回风温度", "空调状态"],
    "antenna": ["天馈编号", "天线类型", "工作频段", "所属站点", "挂高", "方位角", "驻波比", "天馈状态"],
    "transmission": ["设备编号", "传输类型", "带宽容量", "所属站点", "光口状态", "电口状态", "误码率", "设备状态"],
    "feeder": ["馈线编号", "所属站点", "馈线长度", "接头数量", "防水情况", "接地电阻", "巡检日期", "馈线状态"],
    "lightningprot": ["装置编号", "所属站点", "接地电阻", "防雷模块", "浪涌保护", "上次测试", "测试人员", "装置状态"],
    "firealarm": ["设施编号", "设施类型", "所属站点", "灭火剂量", "上次检查", "有效期至", "检查人员", "设施状态"],
    "dooraccess": ["门禁编号", "所属站点", "开门方式", "进出人员", "进出时间", "授权状态", "异常记录", "门禁状态"],
    "patrol": ["任务编号", "巡检站点", "巡检人员", "计划日期", "巡检路线", "发现问题", "处置措施", "任务状态"],
    "fuel": ["记录编号", "所属站点", "油料类型", "调入量", "当前存量", "发电消耗", "油料日期", "油料状态"],
    "rental": ["合同编号", "站点名称", "出租方", "年租金", "签约日期", "到期日期", "续租条款", "合同状态"],
    "electricbill": ["记录编号", "所属站点", "电表读数", "用电量", "电费金额", "缴费月份", "缴费状态", "票据编号"],
    "demolition": ["任务编号", "拆除站点", "拆除原因", "拆除范围", "施工队伍", "计划工期", "物资回收", "任务状态"],
    "emergency": ["保障编号", "保障类型", "保障地点", "通信车编号", "保障人员", "到达时间", "撤离时间", "保障状态"],
    "energyeff": ["项目编号", "所属站点", "改造内容", "预估节电率", "投资金额", "承包单位", "投资回收期", "项目状态"],
}

# 各模块编号前缀：样例数据的编号字段统一按 前缀-序号 生成。
MODULE_CODE_PREFIX: dict[str, str] = {
    "site": "SITE",
    "tower": "TOWE",
    "power": "POWE",
    "battery": "BATT",
    "genset": "GENS",
    "rectifier": "RECT",
    "ac": "AC",
    "antenna": "ANTE",
    "transmission": "TRAN",
    "feeder": "FEED",
    "lightningprot": "LIGH",
    "firealarm": "FIRE",
    "dooraccess": "DOOR",
    "patrol": "PATR",
    "fuel": "FUEL",
    "rental": "RENT",
    "electricbill": "ELEC",
    "demolition": "DEMO",
    "emergency": "EMER",
    "energyeff": "ENER",
}

# 样例行覆盖的状态：正常/关注/异常各一条，停用态由业务动作流转触达。
SAMPLE_STATUSES = [STATUS_NORMAL, STATUS_ATTENTION, STATUS_ABNORMAL]

# 数值型字段的样例取值规则：数量类取 10 的倍数，金额类取 12.5 的倍数。
_COUNT_FIELDS = {"平台数量", "接头数量"}
_MONEY_FIELDS = {"电费金额", "投资金额"}


def _sample_value(module: str, field: str, seq: int) -> Any:
    """按字段名生成样例值：编号、日期、数量、金额各有统一写法。"""
    if field.endswith("编号"):
        return f"{MODULE_CODE_PREFIX[module]}-{seq:04d}"
    if field.endswith(("日期", "时间")):
        return f"2026-09-{seq:02d}"
    if field in _COUNT_FIELDS:
        return seq * 10
    if field in _MONEY_FIELDS:
        return seq * 12.5
    return f"{MODULE_LABELS[module]}样例{seq}"


def build_seed_rows() -> dict[str, list[dict[str, Any]]]:
    """按统一口径生成全部模块的样例行；每次调用返回全新副本。"""
    tables: dict[str, list[dict[str, Any]]] = {}
    for module, fields in MODULE_FIELDS.items():
        rows: list[dict[str, Any]] = []
        for seq, status in enumerate(SAMPLE_STATUSES, start=1):
            row: dict[str, Any] = {"id": seq, "status": status}
            row.update(derive_flags(status))
            for field in fields:
                row[field] = _sample_value(module, field, seq)
            rows.append(row)
        tables[module] = rows
    return tables


SEED_ROWS: dict[str, list[dict[str, Any]]] = build_seed_rows()
