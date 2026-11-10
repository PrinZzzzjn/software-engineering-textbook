import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试用的管理员账号
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# 全局存储访问令牌
ACCESS_TOKEN = None

# 测试用的临时用户信息
TEST_USERNAME = "test_user_api"
TEST_USER_PASSWORD = "test_password123"
TEST_USER_ID = None

def get_admin_token():
    """获取管理员访问令牌"""
    global ACCESS_TOKEN
    if ACCESS_TOKEN:
        return ACCESS_TOKEN
    
    print("获取管理员访问令牌...")
    # 准备登录数据
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    # 发送登录请求
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        ACCESS_TOKEN = data.get("access_token")
        print("✓ 获取管理员访问令牌成功")
        return ACCESS_TOKEN
    else:
        print(f"✗ 获取管理员访问令牌失败: {response.status_code} - {response.text}")
        return None

def get_headers():
    """获取带有访问令牌的请求头"""
    token = get_admin_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_get_users():
    """测试获取用户列表"""
    print("\n测试获取用户列表...")
    
    # 发送请求
    response = requests.get(f"{BASE_URL}/api/v1/users/", headers=get_headers())
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 获取用户列表成功")
        return True
    else:
        print("✗ 获取用户列表失败")
        return False

def test_create_user():
    """测试创建新用户"""
    global TEST_USER_ID
    print("\n测试创建新用户...")
    
    # 准备用户数据
    user_data = {
        "username": TEST_USERNAME,
        "password": TEST_USER_PASSWORD,
        "role": "normal",
        "is_active": 1
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/api/v1/users/", headers=get_headers(), json=user_data)
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 201:
        data = response.json()
        TEST_USER_ID = data.get("id")
        print(f"✓ 创建用户成功，用户ID: {TEST_USER_ID}")
        return True
    else:
        print("✗ 创建用户失败")
        return False

def test_get_user():
    """测试获取单个用户信息"""
    if not TEST_USER_ID:
        print("跳过获取单个用户信息测试（未创建测试用户）")
        return False
    
    print(f"\n测试获取单个用户信息 (ID: {TEST_USER_ID})...")
    
    # 发送请求
    response = requests.get(f"{BASE_URL}/api/v1/users/{TEST_USER_ID}", headers=get_headers())
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 获取单个用户信息成功")
        return True
    else:
        print("✗ 获取单个用户信息失败")
        return False

def test_update_user():
    """测试更新用户信息"""
    if not TEST_USER_ID:
        print("跳过更新用户信息测试（未创建测试用户）")
        return False
    
    print(f"\n测试更新用户信息 (ID: {TEST_USER_ID})...")
    
    # 准备更新数据
    update_data = {
        "role": "admin",
        "is_active": 1
    }
    
    # 发送请求
    response = requests.put(f"{BASE_URL}/api/v1/users/{TEST_USER_ID}", headers=get_headers(), json=update_data)
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 更新用户信息成功")
        return True
    else:
        print("✗ 更新用户信息失败")
        return False

def test_reset_password():
    """测试重置用户密码"""
    if not TEST_USER_ID:
        print("跳过重设用户密码测试（未创建测试用户）")
        return False
    
    print(f"\n测试重置用户密码 (ID: {TEST_USER_ID})...")
    
    # 准备重置密码数据
    reset_data = {
        "new_password": "new_test_password456"
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/api/v1/users/{TEST_USER_ID}/reset-password", headers=get_headers(), json=reset_data)
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 重置用户密码成功")
        return True
    else:
        print("✗ 重置用户密码失败")
        return False

def test_delete_user():
    """测试删除用户"""
    if not TEST_USER_ID:
        print("跳过删除用户测试（未创建测试用户）")
        return False
    
    # 确保不删除管理员账号
    if TEST_USER_ID == 1:
        print("跳过删除用户测试（不能删除管理员账号）")
        return False
    
    print(f"\n测试删除用户 (ID: {TEST_USER_ID})...")
    
    # 发送请求
    response = requests.delete(f"{BASE_URL}/api/v1/users/{TEST_USER_ID}", headers=get_headers())
    
    # 打印响应信息
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print("✓ 删除用户成功")
        return True
    else:
        print("✗ 删除用户失败")
        return False

def cleanup_test_user():
    """清理测试用户（如果测试过程中断）"""
    global TEST_USER_ID
    if TEST_USER_ID and TEST_USER_ID != 1:
        try:
            print(f"\n清理测试用户 (ID: {TEST_USER_ID})...")
            requests.delete(f"{BASE_URL}/api/v1/users/{TEST_USER_ID}", headers=get_headers())
            print("✓ 测试用户清理完成")
        except Exception as e:
            print(f"⚠️  清理测试用户时出错: {e}")

if __name__ == "__main__":
    print("开始测试user模块API...\n")
    
    try:
        # 运行测试
        get_users_result = test_get_users()
        create_user_result = test_create_user()
        get_user_result = test_get_user()
        update_user_result = test_update_user()
        reset_password_result = test_reset_password()
        delete_user_result = test_delete_user()
        
        # 测试总结
        print("\n=== 测试总结 ===")
        print(f"获取用户列表: {'成功' if get_users_result else '失败'}")
        print(f"创建用户: {'成功' if create_user_result else '失败'}")
        print(f"获取单个用户: {'成功' if get_user_result else '失败'}")
        print(f"更新用户: {'成功' if update_user_result else '失败'}")
        print(f"重置密码: {'成功' if reset_password_result else '失败'}")
        print(f"删除用户: {'成功' if delete_user_result else '失败'}")
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    finally:
        # 确保清理测试用户
        cleanup_test_user()
    
    print("\n测试完成！")