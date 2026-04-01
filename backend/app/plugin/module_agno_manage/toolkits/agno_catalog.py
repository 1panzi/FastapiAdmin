# -*- coding: utf-8 -*-
"""
Agno 内置工具目录。

提供 list_agno_tools() 函数，返回所有可用 agno 工具的元数据，
供前端在创建 toolkit 时选择 module_path + class_name。
"""

from typing import TypedDict


class AgnoToolInfo(TypedDict):
    name: str          # 展示名称
    module_path: str   # Python 导入路径
    class_name: str    # 类名
    category: str      # 分类
    description: str   # 简要说明


# Agno 内置工具目录（agno==2.5.x）
_CATALOG: list[AgnoToolInfo] = [
    # ── 搜索与网页 ────────────────────────────────────────────────────────────
    {"name": "DuckDuckGo 搜索", "module_path": "agno.tools.duckduckgo", "class_name": "DuckDuckGoTools", "category": "搜索", "description": "免费 DuckDuckGo 网络搜索"},
    {"name": "Tavily 搜索", "module_path": "agno.tools.tavily", "class_name": "TavilyTools", "category": "搜索", "description": "Tavily AI 搜索（需 API Key）"},
    {"name": "Serper 搜索", "module_path": "agno.tools.serper", "class_name": "SerperTools", "category": "搜索", "description": "Google 搜索 via Serper（需 API Key）"},
    {"name": "SerpAPI 搜索", "module_path": "agno.tools.serpapi", "class_name": "SerpApiTools", "category": "搜索", "description": "SerpAPI Google/Bing 搜索"},
    {"name": "Brave 搜索", "module_path": "agno.tools.bravesearch", "class_name": "BraveSearchTools", "category": "搜索", "description": "Brave 隐私搜索引擎"},
    {"name": "百度搜索", "module_path": "agno.tools.baidusearch", "class_name": "BaiduSearchTools", "category": "搜索", "description": "百度搜索"},
    {"name": "Exa 搜索", "module_path": "agno.tools.exa", "class_name": "ExaTools", "category": "搜索", "description": "Exa 语义搜索"},
    {"name": "Searxng", "module_path": "agno.tools.searxng", "class_name": "Searxng", "category": "搜索", "description": "自托管 Searxng 元搜索"},
    {"name": "Perplexity 搜索", "module_path": "agno.tools.perplexity", "class_name": "PerplexitySearch", "category": "搜索", "description": "Perplexity AI 搜索"},
    {"name": "网站工具", "module_path": "agno.tools.website", "class_name": "WebsiteTools", "category": "搜索", "description": "抓取并读取网站内容"},
    {"name": "网页浏览器", "module_path": "agno.tools.webbrowser", "class_name": "WebBrowserTools", "category": "搜索", "description": "打开网页链接"},
    {"name": "Trafilatura 抓取", "module_path": "agno.tools.trafilatura", "class_name": "TrafilaturaTools", "category": "搜索", "description": "网页正文提取"},
    {"name": "Jina Reader", "module_path": "agno.tools.jina", "class_name": "JinaReaderTools", "category": "搜索", "description": "Jina Reader 网页转 Markdown"},
    {"name": "Spider 爬虫", "module_path": "agno.tools.spider", "class_name": "SpiderTools", "category": "搜索", "description": "Spider.cloud 网页爬取"},
    {"name": "Crawl4AI", "module_path": "agno.tools.crawl4ai", "class_name": "Crawl4aiTools", "category": "搜索", "description": "Crawl4AI 异步网页爬取"},
    {"name": "Firecrawl", "module_path": "agno.tools.firecrawl", "class_name": "FirecrawlTools", "category": "搜索", "description": "Firecrawl 结构化网页抓取"},
    {"name": "ScrapegraphAI", "module_path": "agno.tools.scrapegraph", "class_name": "ScrapeGraphTools", "category": "搜索", "description": "AI 驱动的网页结构化抓取"},

    # ── 知识与数据库 ──────────────────────────────────────────────────────────
    {"name": "Wikipedia", "module_path": "agno.tools.wikipedia", "class_name": "WikipediaTools", "category": "知识", "description": "查询 Wikipedia 百科"},
    {"name": "Arxiv 论文", "module_path": "agno.tools.arxiv", "class_name": "ArxivTools", "category": "知识", "description": "搜索和读取 arXiv 学术论文"},
    {"name": "PubMed 医学", "module_path": "agno.tools.pubmed", "class_name": "PubmedTools", "category": "知识", "description": "PubMed 医学文献搜索"},
    {"name": "HackerNews", "module_path": "agno.tools.hackernews", "class_name": "HackerNewsTools", "category": "知识", "description": "HackerNews 热门文章"},
    {"name": "Newspaper4k", "module_path": "agno.tools.newspaper4k", "class_name": "Newspaper4kTools", "category": "知识", "description": "读取新闻文章"},
    {"name": "SQL 工具", "module_path": "agno.tools.sql", "class_name": "SQLTools", "category": "数据库", "description": "执行 SQL 查询"},
    {"name": "PostgreSQL 工具", "module_path": "agno.tools.postgres", "class_name": "PostgresTools", "category": "数据库", "description": "PostgreSQL 数据库操作"},
    {"name": "DuckDB 工具", "module_path": "agno.tools.duckdb", "class_name": "DuckDbTools", "category": "数据库", "description": "DuckDB 内存分析数据库"},
    {"name": "Pandas 工具", "module_path": "agno.tools.pandas", "class_name": "PandasTools", "category": "数据", "description": "Pandas 数据分析操作"},
    {"name": "CSV 工具", "module_path": "agno.tools.csv_toolkit", "class_name": "CsvTools", "category": "数据", "description": "读写 CSV 文件"},
    {"name": "Google BigQuery", "module_path": "agno.tools.google_bigquery", "class_name": "BigQueryTools", "category": "数据库", "description": "Google BigQuery 数据仓库"},
    {"name": "Redshift", "module_path": "agno.tools.redshift", "class_name": "RedshiftTools", "category": "数据库", "description": "Amazon Redshift 数据仓库"},
    {"name": "Neo4j 图数据库", "module_path": "agno.tools.neo4j", "class_name": "Neo4jTools", "category": "数据库", "description": "Neo4j 图数据库查询"},

    # ── 文件与本地系统 ────────────────────────────────────────────────────────
    {"name": "文件工具", "module_path": "agno.tools.file", "class_name": "FileTools", "category": "文件", "description": "读写本地文件"},
    {"name": "本地文件系统", "module_path": "agno.tools.local_file_system", "class_name": "LocalFileSystemTools", "category": "文件", "description": "本地文件系统操作"},
    {"name": "Shell 工具", "module_path": "agno.tools.shell", "class_name": "ShellTools", "category": "系统", "description": "执行 Shell 命令"},
    {"name": "Python 执行", "module_path": "agno.tools.python", "class_name": "PythonTools", "category": "系统", "description": "执行 Python 代码"},
    {"name": "Docker 工具", "module_path": "agno.tools.docker", "class_name": "DockerTools", "category": "系统", "description": "Docker 容器管理"},
    {"name": "文件生成工具", "module_path": "agno.tools.file_generation", "class_name": "FileGenerationTools", "category": "文件", "description": "生成文件内容"},

    # ── 金融与数据分析 ────────────────────────────────────────────────────────
    {"name": "YFinance 金融", "module_path": "agno.tools.yfinance", "class_name": "YFinanceTools", "category": "金融", "description": "Yahoo Finance 股票数据"},
    {"name": "OpenBB 金融", "module_path": "agno.tools.openbb", "class_name": "OpenBBTools", "category": "金融", "description": "OpenBB 金融数据分析"},
    {"name": "Financial Datasets", "module_path": "agno.tools.financial_datasets", "class_name": "FinancialDatasetsTools", "category": "金融", "description": "金融数据集 API"},

    # ── 通讯与协作 ────────────────────────────────────────────────────────────
    {"name": "邮件工具", "module_path": "agno.tools.email", "class_name": "EmailTools", "category": "通讯", "description": "发送 SMTP 邮件"},
    {"name": "Gmail", "module_path": "agno.tools.gmail", "class_name": "GmailTools", "category": "通讯", "description": "Gmail 邮件操作"},
    {"name": "Slack", "module_path": "agno.tools.slack", "class_name": "SlackTools", "category": "通讯", "description": "Slack 消息发送"},
    {"name": "Telegram", "module_path": "agno.tools.telegram", "class_name": "TelegramTools", "category": "通讯", "description": "Telegram Bot 消息"},
    {"name": "Discord", "module_path": "agno.tools.discord", "class_name": "DiscordTools", "category": "通讯", "description": "Discord 消息"},
    {"name": "Twilio", "module_path": "agno.tools.twilio", "class_name": "TwilioTools", "category": "通讯", "description": "Twilio 短信/语音"},
    {"name": "Resend 邮件", "module_path": "agno.tools.resend", "class_name": "ResendTools", "category": "通讯", "description": "Resend 邮件 API"},
    {"name": "Webex", "module_path": "agno.tools.webex", "class_name": "WebexTools", "category": "通讯", "description": "Cisco Webex 协作"},

    # ── 项目与任务管理 ────────────────────────────────────────────────────────
    {"name": "GitHub", "module_path": "agno.tools.github", "class_name": "GithubTools", "category": "开发", "description": "GitHub 仓库操作"},
    {"name": "GitLab", "module_path": "agno.tools.gitlab", "class_name": "GitlabTools", "category": "开发", "description": "GitLab 操作"},
    {"name": "Jira", "module_path": "agno.tools.jira", "class_name": "JiraTools", "category": "项目管理", "description": "Jira 任务管理"},
    {"name": "Linear", "module_path": "agno.tools.linear", "class_name": "LinearTools", "category": "项目管理", "description": "Linear 任务管理"},
    {"name": "ClickUp", "module_path": "agno.tools.clickup", "class_name": "ClickUpTools", "category": "项目管理", "description": "ClickUp 项目管理"},
    {"name": "Trello", "module_path": "agno.tools.trello", "class_name": "TrelloTools", "category": "项目管理", "description": "Trello 看板"},
    {"name": "Notion", "module_path": "agno.tools.notion", "class_name": "NotionTools", "category": "项目管理", "description": "Notion 笔记/知识库"},
    {"name": "Todoist", "module_path": "agno.tools.todoist", "class_name": "TodoistTools", "category": "项目管理", "description": "Todoist 任务清单"},
    {"name": "Confluence", "module_path": "agno.tools.confluence", "class_name": "ConfluenceTools", "category": "项目管理", "description": "Confluence 文档协作"},
    {"name": "Bitbucket", "module_path": "agno.tools.bitbucket", "class_name": "BitbucketTools", "category": "开发", "description": "Bitbucket 代码仓库"},
    {"name": "Airflow", "module_path": "agno.tools.airflow", "class_name": "AirflowTools", "category": "数据", "description": "Apache Airflow DAG 管理"},

    # ── Google 生态 ───────────────────────────────────────────────────────────
    {"name": "Google 日历", "module_path": "agno.tools.googlecalendar", "class_name": "GoogleCalendarTools", "category": "Google", "description": "Google Calendar 日历管理"},
    {"name": "Google Drive", "module_path": "agno.tools.google_drive", "class_name": "GoogleDriveTools", "category": "Google", "description": "Google Drive 文件管理"},
    {"name": "Google Maps", "module_path": "agno.tools.google_maps", "class_name": "GoogleMapsTools", "category": "Google", "description": "Google Maps 地图服务"},
    {"name": "Google Sheets", "module_path": "agno.tools.googlesheets", "class_name": "GoogleSheetsTools", "category": "Google", "description": "Google Sheets 表格操作"},

    # ── AI 与图像生成 ─────────────────────────────────────────────────────────
    {"name": "DALL-E 图像", "module_path": "agno.tools.dalle", "class_name": "DalleTools", "category": "AI生成", "description": "OpenAI DALL-E 图像生成"},
    {"name": "OpenAI 工具", "module_path": "agno.tools.openai", "class_name": "OpenAITools", "category": "AI生成", "description": "OpenAI 通用工具"},
    {"name": "Replicate", "module_path": "agno.tools.replicate", "class_name": "ReplicateTools", "category": "AI生成", "description": "Replicate AI 模型运行"},
    {"name": "Fal AI", "module_path": "agno.tools.fal", "class_name": "FalTools", "category": "AI生成", "description": "Fal.ai 图像/视频生成"},

    # ── 推理与控制 ────────────────────────────────────────────────────────────
    {"name": "推理工具", "module_path": "agno.tools.reasoning", "class_name": "ReasoningTools", "category": "推理", "description": "CoT 推理辅助工具"},
    {"name": "计算器", "module_path": "agno.tools.calculator", "class_name": "CalculatorTools", "category": "工具", "description": "数学计算器"},
    {"name": "调度工具", "module_path": "agno.tools.scheduler", "class_name": "SchedulerTools", "category": "工具", "description": "定时任务调度"},
    {"name": "Sleep 工具", "module_path": "agno.tools.sleep", "class_name": "SleepTools", "category": "工具", "description": "等待/延迟执行"},
    {"name": "用户控制流", "module_path": "agno.tools.user_control_flow", "class_name": "UserControlFlowTools", "category": "工具", "description": "用户交互控制流"},
    {"name": "用户反馈", "module_path": "agno.tools.user_feedback", "class_name": "UserFeedbackTools", "category": "工具", "description": "收集用户反馈"},
    {"name": "知识库工具", "module_path": "agno.tools.knowledge", "class_name": "KnowledgeTools", "category": "知识", "description": "Agno 知识库搜索/更新"},
    {"name": "记忆工具", "module_path": "agno.tools.memory", "class_name": "MemoryTools", "category": "工具", "description": "Agent 记忆管理"},

    # ── 其他 ──────────────────────────────────────────────────────────────────
    {"name": "YouTube", "module_path": "agno.tools.youtube", "class_name": "YouTubeTools", "category": "媒体", "description": "YouTube 视频信息获取"},
    {"name": "Reddit", "module_path": "agno.tools.reddit", "class_name": "RedditTools", "category": "社交", "description": "Reddit 内容获取"},
    {"name": "X (Twitter)", "module_path": "agno.tools.x", "class_name": "XTools", "category": "社交", "description": "X (Twitter) 内容操作"},
    {"name": "Shopify", "module_path": "agno.tools.shopify", "class_name": "ShopifyTools", "category": "电商", "description": "Shopify 电商操作"},
    {"name": "AWS Lambda", "module_path": "agno.tools.aws_lambda", "class_name": "AWSLambdaTools", "category": "云服务", "description": "调用 AWS Lambda 函数"},
    {"name": "自定义 API", "module_path": "agno.tools.api", "class_name": "CustomApiTools", "category": "工具", "description": "调用自定义 REST API"},
    {"name": "OpenWeather", "module_path": "agno.tools.openweather", "class_name": "OpenWeatherTools", "category": "工具", "description": "OpenWeatherMap 天气查询"},
    {"name": "Zendesk", "module_path": "agno.tools.zendesk", "class_name": "ZendeskTools", "category": "客服", "description": "Zendesk 工单管理"},
    {"name": "Zoom", "module_path": "agno.tools.zoom", "class_name": "ZoomTools", "category": "通讯", "description": "Zoom 会议管理"},
    {"name": "Spotify", "module_path": "agno.tools.spotify", "class_name": "SpotifyTools", "category": "媒体", "description": "Spotify 音乐搜索/控制"},
    {"name": "Google Giphy", "module_path": "agno.tools.giphy", "class_name": "GiphyTools", "category": "媒体", "description": "Giphy GIF 搜索"},
    {"name": "Apify 爬虫", "module_path": "agno.tools.apify", "class_name": "ApifyTools", "category": "搜索", "description": "Apify 平台网页爬取"},
    {"name": "Eleven Labs 语音", "module_path": "agno.tools.eleven_labs", "class_name": "ElevenLabsTools", "category": "AI生成", "description": "ElevenLabs 文字转语音"},
    {"name": "Coding 工具", "module_path": "agno.tools.coding", "class_name": "CodingTools", "category": "开发", "description": "代码生成/执行辅助"},
    {"name": "E2B 代码执行", "module_path": "agno.tools.e2b", "class_name": "E2BTools", "category": "开发", "description": "E2B 安全代码执行沙箱"},
    {"name": "Daytona", "module_path": "agno.tools.daytona", "class_name": "DaytonaTools", "category": "开发", "description": "Daytona 开发环境管理"},
    {"name": "可视化工具", "module_path": "agno.tools.visualization", "class_name": "VisualizationTools", "category": "数据", "description": "数据可视化图表生成"},
    {"name": "Docling 文档解析", "module_path": "agno.tools.docling", "class_name": "DoclingTools", "category": "文件", "description": "Docling 文档结构化解析"},
    {"name": "OpenCV 图像", "module_path": "agno.tools.opencv", "class_name": "OpenCVTools", "category": "AI生成", "description": "OpenCV 图像处理"},
    {"name": "Cal.com 日历", "module_path": "agno.tools.calcom", "class_name": "CalComTools", "category": "通讯", "description": "Cal.com 日程预约"},
    {"name": "Zep 记忆", "module_path": "agno.tools.zep", "class_name": "ZepTools", "category": "工具", "description": "Zep 长期记忆管理"},
    {"name": "Linkup 搜索", "module_path": "agno.tools.linkup", "class_name": "LinkupTools", "category": "搜索", "description": "Linkup 实时网络搜索"},
    {"name": "Brandfetch", "module_path": "agno.tools.brandfetch", "class_name": "BrandfetchTools", "category": "工具", "description": "品牌信息查询"},
]


def list_agno_tools(category: str | None = None, keyword: str | None = None) -> list[AgnoToolInfo]:
    """返回 agno 内置工具目录，支持按分类和关键词过滤。"""
    result = _CATALOG
    if category:
        result = [t for t in result if t["category"] == category]
    if keyword:
        kw = keyword.lower()
        result = [t for t in result if kw in t["name"].lower() or kw in t["description"].lower()]
    return result


def get_categories() -> list[str]:
    """返回所有分类列表（去重有序）。"""
    seen: set[str] = set()
    cats: list[str] = []
    for t in _CATALOG:
        if t["category"] not in seen:
            seen.add(t["category"])
            cats.append(t["category"])
    return cats
