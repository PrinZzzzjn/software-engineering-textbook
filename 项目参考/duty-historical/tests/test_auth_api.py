import pytest
from fastapi.testclient import TestClient
from app.main import app

# 创建测试客户端
client = TestClient(app)

class TestAuthAPI:
    """认证API测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 测试用的管理员账号（默认存在）
        self.admin_username = "admin"
        self.admin_password = "admin123"
        
        # 存储登录后的令牌
        self.access_token = None
        self.refresh_token = None
    
    def test_login_success(self):
        """测试成功登录"""
        # 准备登录数据
        login_data = {
            "username": self.admin_username,
            "password": self.admin_password
        }
        
        # 发送登录请求
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # 验证响应状态码
        assert response.status_code == 200
        
        # 验证响应数据结构
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data
        
        # 验证用户信息
        assert data["user"]["username"] == self.admin_username
        assert data["user"]["role"] == "admin"
        
        # 保存令牌供后续测试使用
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]