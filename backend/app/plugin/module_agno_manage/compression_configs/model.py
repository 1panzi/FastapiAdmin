
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgCompressionConfigModel(ModelMixin, UserMixin):
    """
    压缩管理器表
    """
    __tablename__: str = 'ag_compression_configs'
    __table_args__: dict[str, str] = {'comment': '压缩管理器'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='压缩配置名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联压缩模型ID')
    compress_tool_results_limit: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='触发工具结果压缩的条数阈值')
    compress_token_limit: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='触发压缩的Token数阈值')
    compress_tool_call_instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='工具调用压缩指令')
