"""
YoutubeReaderBuilder — YouTube 视频字幕 Reader Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class YoutubeReaderBuilder(BaseReaderBuilder):
    type = "youtube"
    label = "YouTube Reader"
    agno_class = None  # 延迟导入

    extra_fields = [
        *BaseReaderBuilder.extra_fields,
        {"name": "language", "type": "str", "required": False, "default": "en", "order": 20},
    ]
    field_meta = {
        **BaseReaderBuilder.field_meta,
        "language": {
            "label": "字幕语言",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 en / zh-Hans",
            "tooltip": "YouTube 字幕语言代码",
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.youtube import YoutubeReader

        kwargs = self._get_chunker_kwargs(config)
        if config.get("language"):
            kwargs["language"] = config["language"]
        return YoutubeReader(**kwargs)
