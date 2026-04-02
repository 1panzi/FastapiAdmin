
from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgToolkitModel(ModelMixin, UserMixin):
    """
    工具管理表
    """
    __tablename__: str = 'ag_toolkits'
    __table_args__: dict[str, str] = {'comment': '工具管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='工具包名称')
    type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='类型(toolkit:整个类 function:单个函数 code:代码工具)')
    module_path: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='Python模块路径（type=code时为空）')
    class_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='类名（type=toolkit时使用）')
    func_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='函数名（type=function时使用）')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='初始化参数')
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='工具使用说明')
    requires_confirmation: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否需要确认')
    approval_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='审批类型(NULL/required/audit)')
    stop_after_call: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='调用后是否停止')
    show_result: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否展示结果')
    cache_results: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否缓存结果')
    cache_ttl: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='缓存TTL秒数')
    tool_from: Mapped[str | None] = mapped_column(String(20), nullable=True, default='agno', comment='工具来源(agno/custom/code)')
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, comment='工具分类')
    global_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment='超管全局开关，False时所有用户不可见不可用')
    source_code: Mapped[str | None] = mapped_column(Text, nullable=True, comment='预留：type=code时存Python源码')
    param_schema: Mapped[list | None] = mapped_column(JSON, nullable=True, comment='参数描述列表，每项含 name/type/default/required')
