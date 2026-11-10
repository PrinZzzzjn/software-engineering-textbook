# 简单测试脚本
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

# 导入项目相关模块
import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.core.database import SessionLocal
from app.api.v1.module_duty.holiday.models import Holiday, HolidayType
from jose import jwt
from app.config.setting import settings

# 创建测试客户端
client = TestClient(app)

# 生成测试用的JWT令牌
def create_test_token(user_id="test_user", role="admin"):
    """创建测试用的JWT令牌"""
    # 创建payload
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    # 生成令牌
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# 获取带有认证头的请求头
def get_auth_headers(role="admin"):
    """获取带有认证头的请求头"""
    token = create_test_token(role=role)
    return {
        "Authorization": f"Bearer {token}"
    }

# 清理测试数据
def cleanup_test_data():
    db = SessionLocal()
    try:
        # 清理2024年的测试数据
        db.query(Holiday).filter(
            Holiday.date >= date(2024, 1, 1),
            Holiday.date <= date(2024, 12, 31)
        ).delete()
        db.commit()
    finally:
        db.close()

# 直接在测试中创建节假日数据

# 测试获取节假日列表
def test_get_holidays():
    print("测试获取节假日列表...")
    
    # 获取认证头
    headers = get_auth_headers()
    
    # 发送请求
    response = client.get("/api/v1/holidays", headers=headers)
    
    # 验证响应
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    
    print("获取节假日列表测试通过")

# 测试创建节假日
def test_create_holiday():
    print("测试创建节假日...")
    
    # 获取管理员认证头（创建节假日需要管理员权限）
    headers = get_auth_headers(role="admin")
    
    # 测试数据
    holiday_data = {
        "date": "2024-02-10",
        "is_holiday": True,
        "name": "春节",
        "holiday_type": "01",  # 使用枚举值'01'代表法定假日
        "description": "中国传统节日"
    }
    
    # 发送请求
    response = client.post("/api/v1/holidays", json=holiday_data, headers=headers)
    
    # 验证响应
    print(f"创建响应状态码: {response.status_code}")
    print(f"创建响应内容: {response.text}")
    
    assert response.status_code == 201  # 创建成功应该返回201
    data = response.json()
    assert data["date"] == "2024-02-10"
    assert data["name"] == "春节"
    
    print("创建节假日测试通过")

# 暂时注释其他测试，先确保基本功能









# 运行测试
if __name__ == "__main__":
    try:
        # 清理测试数据
        cleanup_test_data()
        
        # 运行基本测试
        test_get_holidays()
        test_create_holiday()
        
        print("所有测试通过！")
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        # 清理测试数据
        cleanup_test_data()
