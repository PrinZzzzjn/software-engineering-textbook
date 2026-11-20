import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
DEPARTMENTS_URL = f"{BASE_URL}/departments"

# 登录获取访问令牌
def login():
    """用户登录获取访问令牌"""
    login_data = {
        "username": "admin",  # 假设的管理员用户名
        "password": "admin123"  # 假设的管理员密码
    }
    
    print("尝试登录获取访问令牌...")
    print(f"登录数据: {login_data}")
    
    try:
        response = requests.post(
            LOGIN_URL,
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            if access_token:
                print("✅ 登录成功，获取到访问令牌！")
                return access_token
        
        print("❌ 登录失败或未获取到访问令牌！")
        return None
        
    except Exception as e:
        print(f"❌ 登录请求出错: {str(e)}")
        return None

# 测试创建部门
def test_create_department():
    # 首先登录获取访问令牌
    access_token = login()
    if not access_token:
        print("❌ 无法继续测试，因为未获取到有效的访问令牌")
        return
    
    # 测试数据
    dept_data = {
        "full_name": "测试部门",
        "address": "测试地址",
        "longitude": 116.4074,
        "latitude": 39.9042,
        "parent_dept_code": None  # 创建根部门，不指定父部门
    }
    
    print("\n测试创建部门API...")
    print(f"请求数据: {dept_data}")
    
    # 添加认证头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            DEPARTMENTS_URL,
            json=dept_data,
            headers=headers
        )
        
        # 打印响应信息
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✅ 创建部门成功！")
        else:
            print("❌ 创建部门失败！")
            
    except Exception as e:
        print(f"❌ 请求出错: {str(e)}")

if __name__ == "__main__":
    test_create_department()