"""业务模块登记表：字段名、状态取值、可执行动作的唯一出处。

种子数据、业务规则、接口与前端页面都从这里取同一套口径；
任何模块要改字段或状态，只改这一处，其他地方自动跟上。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StatCard:
    """模块页顶部统计卡：label 是展示文案，status 用来从同一份数据里数出数值。"""

    label: str
    status: str


@dataclass(frozen=True)
class ModuleSpec:
    """一个业务模块的共用口径。"""

    key: str  # 路由与存储用的模块键
    title: str  # 模块中文名：概览、页头、提示语共用
    noun: str  # 单条记录的称呼，用于提示语
    fields: tuple[str, ...]  # 列表与明细共用的一套中文字段名
    statuses: tuple[str, ...]  # 状态取值全集，按流转顺序排列，末位为终态
    actions: dict[str, str]  # 动作 -> 目标状态
    stats: tuple[StatCard, ...]  # 模块页统计卡口径
    negative_actions: tuple[str, ...] = ()  # 执行后计入异常量的动作

    @property
    def required_fields(self) -> list[str]:
        """登记时必填的字段，统一取前三个。"""
        return list(self.fields[:3])

    @property
    def keyword_field(self) -> str:
        """列表关键字检索命中的字段，统一取第一个（编号列）。"""
        return self.fields[0]


MODULE_SPECS: dict[str, ModuleSpec] = {
    spec.key: spec
    for spec in [
        ModuleSpec(
            key="site",
            title="基站台账",
            noun="基站",
            fields=("基站编号", "基站名称", "基站类型", "所属区县", "经纬度坐标", "铁塔高度", "入网日期", "基站状态"),
            statuses=("运行中", "退服中", "已退网", "已拆除"),
            actions={"登记退服": "退服中", "申请退网": "已退网", "拆站完成": "已拆除"},
            stats=(StatCard("运行基站", "运行中"), StatCard("退服基站", "退服中"), StatCard("退网站点", "已退网")),
        ),
        ModuleSpec(
            key="tower",
            title="铁塔管理",
            noun="铁塔",
            fields=("铁塔编号", "铁塔类型", "设计高度", "平台数量", "所属站点", "建成年份", "上次检测", "铁塔状态"),
            statuses=("正常", "倾斜超标", "锈蚀", "已拆除"),
            actions={"登记倾斜": "倾斜超标", "防腐处理": "锈蚀", "拆塔完成": "已拆除"},
            stats=(StatCard("正常铁塔", "正常"), StatCard("倾斜铁塔", "倾斜超标"), StatCard("锈蚀铁塔", "锈蚀")),
        ),
        ModuleSpec(
            key="power",
            title="动力配套",
            noun="电源设备",
            fields=("设备编号", "设备类型", "额定功率", "所属站点", "投用日期", "上次检修", "下次检修日", "设备状态"),
            statuses=("正常运行", "降额运行", "故障停机", "已报废"),
            actions={"降额运行": "降额运行", "故障停机": "故障停机", "申请报废": "已报废"},
            stats=(StatCard("正常设备", "正常运行"), StatCard("降额设备", "降额运行"), StatCard("故障设备", "故障停机")),
        ),
        ModuleSpec(
            key="battery",
            title="蓄电池组",
            noun="蓄电池组",
            fields=("电池组编号", "电池类型", "额定容量", "所属站点", "放电时长", "内阻值", "投用日期", "电池状态"),
            statuses=("容量合格", "容量下降", "需更换", "已更换"),
            actions={"记录下降": "容量下降", "安排更换": "需更换", "完成更换": "已更换"},
            stats=(StatCard("合格电池组", "容量合格"), StatCard("下降电池组", "容量下降"), StatCard("需更换电池组", "需更换")),
        ),
        ModuleSpec(
            key="genset",
            title="发电机组",
            noun="发电机组",
            fields=("机组编号", "机组型号", "额定功率", "所属站点", "上次试机", "油量储备", "启动状态", "机组状态"),
            statuses=("待命", "发电中", "故障", "维修中"),
            actions={"启动发电": "发电中", "关闭机组": "待命", "登记故障": "维修中"},
            stats=(StatCard("待命机组", "待命"), StatCard("发电机组", "发电中"), StatCard("故障机组", "故障")),
        ),
        ModuleSpec(
            key="rectifier",
            title="开关电源",
            noun="开关电源",
            fields=("电源编号", "额定功率", "所属站点", "整流模块数", "负载率", "输出电压", "模块故障", "电源状态"),
            statuses=("正常", "模块缺失", "输出异常", "已更换"),
            actions={"记录缺失": "模块缺失", "记录异常": "输出异常", "安排更换": "已更换"},
            stats=(StatCard("正常电源", "正常"), StatCard("异常电源", "输出异常"), StatCard("模块缺失电源", "模块缺失")),
        ),
        ModuleSpec(
            key="ac",
            title="空调管理",
            noun="空调",
            fields=("空调编号", "空调类型", "制冷量", "所属站点", "运行电流", "设定温度", "回风温度", "空调状态"),
            statuses=("正常", "制冷不足", "压缩机故障", "已更换"),
            actions={"登记不足": "制冷不足", "登记故障": "压缩机故障", "安排更换": "已更换"},
            stats=(StatCard("正常空调", "正常"), StatCard("制冷不足", "制冷不足"), StatCard("故障空调", "压缩机故障")),
        ),
        ModuleSpec(
            key="antenna",
            title="天馈系统",
            noun="天馈设备",
            fields=("天馈编号", "天线类型", "工作频段", "所属站点", "挂高", "方位角", "驻波比", "天馈状态"),
            statuses=("正常", "驻波异常", "下倾偏移", "已调整"),
            actions={"记录异常": "驻波异常", "记录偏移": "下倾偏移", "安排调整": "已调整"},
            stats=(StatCard("正常天馈", "正常"), StatCard("驻波异常数", "驻波异常"), StatCard("偏移天馈数", "下倾偏移")),
        ),
        ModuleSpec(
            key="transmission",
            title="传输设备",
            noun="传输设备",
            fields=("设备编号", "传输类型", "带宽容量", "所属站点", "光口状态", "电口状态", "误码率", "设备状态"),
            statuses=("正常", "光口告警", "误码超标", "已修复"),
            actions={"记录告警": "光口告警", "记录误码": "误码超标", "安排修复": "已修复"},
            stats=(StatCard("正常传输", "正常"), StatCard("告警传输", "光口告警"), StatCard("误码超标传输", "误码超标")),
        ),
        ModuleSpec(
            key="feeder",
            title="馈线巡检",
            noun="馈线",
            fields=("馈线编号", "所属站点", "馈线长度", "接头数量", "防水情况", "接地电阻", "巡检日期", "馈线状态"),
            statuses=("正常", "防水失效", "接地超标", "已修复"),
            actions={"登记失效": "防水失效", "登记超标": "接地超标", "安排修复": "已修复"},
            stats=(StatCard("正常馈线", "正常"), StatCard("失效馈线", "防水失效"), StatCard("超标馈线", "接地超标")),
        ),
        ModuleSpec(
            key="lightningprot",
            title="防雷接地",
            noun="防雷装置",
            fields=("装置编号", "所属站点", "接地电阻", "防雷模块", "浪涌保护", "上次测试", "测试人员", "装置状态"),
            statuses=("合格", "电阻超标", "模块劣化", "已更换"),
            actions={"记录超标": "电阻超标", "记录劣化": "模块劣化", "安排更换": "已更换"},
            stats=(StatCard("合格装置", "合格"), StatCard("超标装置", "电阻超标"), StatCard("劣化装置", "模块劣化")),
        ),
        ModuleSpec(
            key="firealarm",
            title="消防设施",
            noun="消防设施",
            fields=("设施编号", "设施类型", "所属站点", "灭火剂量", "上次检查", "有效期至", "检查人员", "设施状态"),
            statuses=("合格", "压力不足", "已过期", "已更换"),
            actions={"登记不足": "压力不足", "登记过期": "已过期", "安排更换": "已更换"},
            stats=(StatCard("合格设施", "合格"), StatCard("不足设施", "压力不足"), StatCard("过期设施", "已过期")),
        ),
        ModuleSpec(
            key="dooraccess",
            title="门禁管理",
            noun="门禁记录",
            fields=("门禁编号", "所属站点", "开门方式", "进出人员", "进出时间", "授权状态", "异常记录", "门禁状态"),
            statuses=("正常", "授权过期", "非法闯入", "已修复"),
            actions={"续期授权": "授权过期", "记录闯入": "非法闯入", "修复门禁": "已修复"},
            stats=(StatCard("正常门禁", "正常"), StatCard("过期门禁", "授权过期"), StatCard("闯入记录", "非法闯入")),
        ),
        ModuleSpec(
            key="patrol",
            title="巡检作业",
            noun="巡检任务",
            fields=("任务编号", "巡检站点", "巡检人员", "计划日期", "巡检路线", "发现问题", "处置措施", "任务状态"),
            statuses=("待巡检", "巡检中", "已巡检", "待复查"),
            actions={"开始巡检": "巡检中", "提交巡检": "已巡检", "发起复查": "待复查"},
            stats=(StatCard("待巡检站点", "待巡检"), StatCard("已巡检站点", "已巡检"), StatCard("待复查站点", "待复查")),
        ),
        ModuleSpec(
            key="fuel",
            title="油料管理",
            noun="油料记录",
            fields=("记录编号", "所属站点", "油料类型", "调入量", "当前存量", "发电消耗", "油料日期", "油料状态"),
            statuses=("储备充足", "油量偏低", "需补油", "已补充"),
            actions={"记录消耗": "油量偏低", "申请补油": "需补油", "完成补油": "已补充"},
            stats=(StatCard("储备充足站点", "储备充足"), StatCard("油量偏低站点", "油量偏低"), StatCard("需补油站点", "需补油")),
        ),
        ModuleSpec(
            key="rental",
            title="场租合同",
            noun="场租合同",
            fields=("合同编号", "站点名称", "出租方", "年租金", "签约日期", "到期日期", "续租条款", "合同状态"),
            statuses=("执行中", "即将到期", "续租中", "已到期"),
            actions={"登记到期": "即将到期", "申请续租": "续租中", "确认到期": "已到期"},
            stats=(StatCard("执行中合同", "执行中"), StatCard("到期合同", "即将到期"), StatCard("续租合同", "续租中")),
        ),
        ModuleSpec(
            key="electricbill",
            title="电费管理",
            noun="电费记录",
            fields=("记录编号", "所属站点", "电表读数", "用电量", "电费金额", "缴费月份", "缴费状态", "票据编号"),
            statuses=("待缴费", "已缴费", "电费异常", "已核实"),
            actions={"缴纳电费": "已缴费", "登记异常": "电费异常", "核实确认": "已核实"},
            stats=(StatCard("待缴费站点", "待缴费"), StatCard("已缴费站点", "已缴费"), StatCard("异常站点", "电费异常")),
        ),
        ModuleSpec(
            key="demolition",
            title="拆站管理",
            noun="拆站任务",
            fields=("任务编号", "拆除站点", "拆除原因", "拆除范围", "施工队伍", "计划工期", "物资回收", "任务状态"),
            statuses=("待审批", "已批复", "拆除中", "已拆除"),
            actions={"提交审批": "已批复", "开始拆除": "拆除中", "回收完成": "已拆除"},
            stats=(StatCard("待审批拆站", "待审批"), StatCard("拆除中站点", "拆除中"), StatCard("已拆除站点", "已拆除")),
        ),
        ModuleSpec(
            key="emergency",
            title="应急通信",
            noun="应急保障",
            fields=("保障编号", "保障类型", "保障地点", "通信车编号", "保障人员", "到达时间", "撤离时间", "保障状态"),
            statuses=("待响应", "响应中", "保障中", "已撤离"),
            actions={"启动响应": "响应中", "调派车辆": "保障中", "撤离保障": "已撤离"},
            stats=(StatCard("待响应任务", "待响应"), StatCard("保障中任务", "保障中"), StatCard("已撤离任务", "已撤离")),
        ),
        ModuleSpec(
            key="energyeff",
            title="节能改造",
            noun="节能项目",
            fields=("项目编号", "所属站点", "改造内容", "预估节电率", "投资金额", "承包单位", "投资回收期", "项目状态"),
            statuses=("待立项", "改造中", "评估中", "已验收"),
            actions={"申请立项": "改造中", "开始改造": "评估中", "验收评估": "已验收"},
            stats=(StatCard("待立项项目", "待立项"), StatCard("改造中项目", "改造中"), StatCard("已验收项目", "已验收")),
        ),
    ]
}
