import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试用的管理员账号
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_login():
    """测试登录功能"""
    print("测试登录功能...")
    # 准备登录数据
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    # 发送登录请求
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 验证响应
    if response.status_code == 200:
        print("✓ 登录成功")
        data = response.json()
        return data.get("access_token"), data.get("refresh_token")
    else:
        print("✗ 登录失败")
        return None, None

def test_get_current_user(access_token):
    """测试获取当前用户信息"""
    if not access_token:
        print("跳过获取用户信息测试（未获取到访问令牌）")
        return
    
    print("\n测试获取当前用户信息...")
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 发送请求
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 获取用户信息成功")
    else:
        print("✗ 获取用户信息失败")

def test_logout(access_token):
    """测试登出功能"""
    if not access_token:
        print("跳过登出测试（未获取到访问令牌）")
        return
    
    print("\n测试登出功能...")
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers)
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 登出成功")
    else:
        print("✗ 登出失败")

if __name__ == "__main__":
    print("开始测试auth模块API...\n")
    
    # 运行测试
    access_token, refresh_token = test_login()
    test_get_current_user(access_token)
    test_logout(access_token)
    
    print("\n测试完成！")