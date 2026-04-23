#!/usr/bin/env python3
"""
菜单初始化脚本
用法：python create_menus.py
"""

import requests
import json

BASE_URL = "http://192.168.124.162:5180"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJuYW1lXCI6XCJcdThkODVcdTdlYTdcdTdiYTFcdTc0MDZcdTU0NThcIixcInNlc3Npb25faWRcIjpcImZjZWQ4ODM5LTRmZmYtNDBmNy1hNTBlLTQ4OGU0YmY1YTZkNVwiLFwidXNlcl9pZFwiOjEsXCJ1c2VyX25hbWVcIjpcImFkbWluXCIsXCJpcGFkZHJcIjpcIjEyNy4wLjAuMVwiLFwibG9naW5fbG9jYXRpb25cIjpcIlx1NTE4NVx1N2Y1MUlQXCIsXCJvc1wiOlwiV2luZG93c1wiLFwiYnJvd3NlclwiOlwiQ2hyb21lXCIsXCJsb2dpbl90aW1lXCI6XCIyMDI2LTA0LTIzIDEzOjM3OjI0XCIsXCJsb2dpbl90eXBlXCI6XCJQQ1x1N2FlZlwifSIsImlzX3JlZnJlc2giOmZhbHNlLCJleHAiOjE3NzY5NTMyNDN9.70JAqbh1Gg8pZDu9wTbsFym2ct0ru_lX3rLYUZ8Qn-Q"

PARENT_ID = 156

MENUS = [
    {"name": "智能体", "title": "智能体", "route_name": "Agents",          "route_path": "/agno/agents",          "component_path": "module_agno_manage/agno_v2/agents/index",          "order": 1},
    {"name": "压缩",   "title": "压缩",   "route_name": "Compress",         "route_path": "/agno/compress",         "component_path": "module_agno_manage/agno_v2/compress/index",         "order": 2},
    {"name": "文化",   "title": "文化",   "route_name": "Culture",           "route_path": "/agno/culture",          "component_path": "module_agno_manage/agno_v2/culture/index",          "order": 3},
    {"name": "嵌入器", "title": "嵌入器", "route_name": "Embedders",         "route_path": "/agno/embedders",        "component_path": "module_agno_manage/agno_v2/embedders/index",        "order": 4},
    {"name": "安全护栏","title": "安全护栏","route_name": "Guardrails",       "route_path": "/agno/guardrails",       "component_path": "module_agno_manage/agno_v2/guardrails/index",       "order": 5},
    {"name": "知识",   "title": "知识",   "route_name": "Knowledge",         "route_path": "/agno/knowledge",        "component_path": "module_agno_manage/agno_v2/knowledge/index",        "order": 6},
    {"name": "学习",   "title": "学习",   "route_name": "Learn",             "route_path": "/agno/learn",            "component_path": "module_agno_manage/agno_v2/learn/index",            "order": 7},
    {"name": "记忆",   "title": "记忆",   "route_name": "Memory",            "route_path": "/agno/memory",           "component_path": "module_agno_manage/agno_v2/memory/index",           "order": 8},
    {"name": "模型",   "title": "模型",   "route_name": "Models",            "route_path": "/agno/models",           "component_path": "module_agno_manage/agno_v2/models/index",           "order": 9},
    {"name": "阅读器", "title": "阅读器", "route_name": "Readers",           "route_path": "/agno/readers",          "component_path": "module_agno_manage/agno_v2/readers/index",          "order": 10},
    {"name": "推理",   "title": "推理",   "route_name": "Reasoning",         "route_path": "/agno/reasoning",        "component_path": "module_agno_manage/agno_v2/reasoning/index",        "order": 11},
    {"name": "会话摘要","title": "会话摘要","route_name": "Session_summary",  "route_path": "/agno/session_summary",  "component_path": "module_agno_manage/agno_v2/session_summary/index",  "order": 12},
    {"name": "技能",   "title": "技能",   "route_name": "Skills",            "route_path": "/agno/skills",           "component_path": "module_agno_manage/agno_v2/skills/index",           "order": 13},
    {"name": "团队",   "title": "团队",   "route_name": "Teams",             "route_path": "/agno/teams",            "component_path": "module_agno_manage/agno_v2/teams/index",            "order": 14},
    {"name": "工具包", "title": "工具包", "route_name": "Toolkits",          "route_path": "/agno/toolkits",         "component_path": "module_agno_manage/agno_v2/toolkits/index",         "order": 15},
]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json;charset=UTF-8",
}


def create_menu(menu: dict) -> dict:
    payload = {
        "name": menu["name"],
        "type": 2,
        "order": menu["order"],
        "permission": "",
        "route_name": menu["route_name"],
        "route_path": menu["route_path"],
        "component_path": menu["component_path"],
        "redirect": "",
        "parent_id": PARENT_ID,
        "keep_alive": False,
        "hidden": False,
        "always_show": False,
        "title": menu["title"],
        "params": [],
        "affix": False,
        "status": "0",
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/system/menu/create",
        headers=HEADERS,
        json=payload,
        verify=False,
    )
    return resp.json()


def main():
    import urllib3
    import time
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print(f"共 {len(MENUS)} 个菜单，开始创建...\n")
    success, skipped, failed = 0, 0, 0
    for i, menu in enumerate(MENUS):
        if i > 0:
            time.sleep(6)
        while True:
            result = create_menu(menu)
            code = result.get("code")
            msg = result.get("msg", "")
            if code == 200 or code == 0:
                print(f"  [OK]   {menu['name']} (order={menu['order']})")
                success += 1
                break
            elif "已存在" in msg:
                print(f"  [SKIP] {menu['name']} → 已存在，跳过")
                skipped += 1
                break
            elif code == -1 and result.get("data", {}) and result["data"].get("Retry-After"):
                wait = min(int(result["data"]["Retry-After"]), 30)
                print(f"  [WAIT] {menu['name']} → 频率限制，等待 {wait}s ...")
                time.sleep(wait)
            else:
                print(f"  [FAIL] {menu['name']} → {result}")
                failed += 1
                break

    print(f"\n完成：成功 {success}，跳过 {skipped}，失败 {failed}")


if __name__ == "__main__":
    main()
