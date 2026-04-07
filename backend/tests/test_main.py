"""
测试文件

注意：使用普通的 def 定义测试函数，不要使用 async def
执行命令: pytest tests/test.py
"""

import pytest
from fastapi.testclient import TestClient



def test_check_health(test_client: TestClient) -> None:
    """测试健康检查接口"""
    response = test_client.get("/common/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["success"] is True
    assert data["msg"] == "系统健康"
    assert data["data"] is True


# 运行所有测试
if __name__ == "__main__":
    import os
    # 确保 rootdir 始终指向 backend/，无论 IDE 从哪里调起
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pytest.main(["-v", __file__, f"--rootdir={backend_dir}"])
