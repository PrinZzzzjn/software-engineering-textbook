import requests
import json
import time
import random

# API基础URL
BASE_URL = "http://localhost:8000/api/v1/departments"
LOGIN_URL = "http://localhost:8000/api/v1/auth/login"

# 测试账号 - 管理员账号（用于需要管理员权限的操作）
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# 测试账号 - 普通用户账号（用于需要普通用户权限的操作）
USER_USERNAME = "testuser"
USER_PASSWORD = "test123"

# 用于存储测试中创建的部门编码，便于后续更新和删除操作
test_dept_code = None

def login(username, password):
    """登录获取访问令牌"""
    print(f"正在使用账号 {username} 登录...")
    try:
        response = requests.post(
            LOGIN_URL,
            json={"username": username, "password": password}
        )
        response.raise_for_status()  # 检查响应状态码
        data = response.json()
        print(f"登录成功，获取到令牌: {data['access_token'][:20]}...")
        return data['access_token']
    except Exception as e:
        print(f"登录失败: {e}")
        print(f"响应内容: {response.text if 'response' in locals() else '无'}")
        return None

def test_get_departments(token):
    """测试获取部门列表"""
    print("\n测试获取部门列表...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(BASE_URL, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_get_department_tree(token):
    """测试获取部门树形结构"""
    print("\n测试获取部门树形结构...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/tree", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_create_department(token):
    """测试创建部门（需要管理员权限）"""
    global test_dept_code
    print("\n测试创建部门...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 生成随机部门编码，避免重复
    random_number = random.randint(1000, 9999)
    test_dept_code = f"TEST_DEPT_{random_number}"
    
    department_data = {
        "dept_code": test_dept_code,
        "full_name": f"测试部门{random_number}",
        "address": "北京市海淀区测试地址",
        "longitude": 116.397,
        "latitude": 39.908,
        "parent_dept_code": None
    }
    
    print(f"创建部门数据: {department_data}")
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=department_data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 201:
            print(f"部门创建成功，部门编码: {test_dept_code}")
            return True
        else:
            return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_get_department_detail(token):
    """测试获取单个部门详情"""
    global test_dept_code
    if not test_dept_code:
        print("\n无法测试获取部门详情：没有可用的测试部门编码")
        return False
    
    print(f"\n测试获取部门详情（编码: {test_dept_code}）...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/{test_dept_code}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_update_department(token):
    """测试更新部门信息（需要管理员权限）"""
    global test_dept_code
    if not test_dept_code:
        print("\n无法测试更新部门：没有可用的测试部门编码")
        return False
    
    print(f"\n测试更新部门信息（编码: {test_dept_code}）...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "full_name": f"更新后的测试部门_{test_dept_code}",
        "address": "北京市朝阳区更新后的测试地址",
        "longitude": 116.407,
        "latitude": 39.918
    }
    
    try:
        response = requests.put(f"{BASE_URL}/{test_dept_code}", headers=headers, json=update_data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_delete_department(token):
    """测试删除部门（需要管理员权限）"""
    global test_dept_code
    if not test_dept_code:
        print("\n无法测试删除部门：没有可用的测试部门编码")
        return False
    
    print(f"\n测试删除部门（编码: {test_dept_code}）...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/{test_dept_code}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print(f"部门删除成功")
            return True
        else:
            return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def run_dept_api_tests():
    """运行所有部门API测试"""
    print("===== 部门模块API测试开始 =====\n")
    
    # 1. 使用普通用户登录，测试需要普通用户权限的接口
    user_token = login(USER_USERNAME, USER_PASSWORD)
    if not user_token:
        print("无法获取普通用户令牌，跳过需要普通用户权限的测试")
    else:
        # 测试获取部门列表
        test_get_departments(user_token)
        
        # 测试获取部门树形结构
        test_get_department_tree(user_token)
    
    # 2. 使用管理员登录，测试所有接口（包括需要管理员权限的操作）
    admin_token = login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not admin_token:
        print("\n无法获取管理员令牌，测试终止")
        return
    
    # 测试CRUD操作流程
    try:
        # 创建部门
        if test_create_department(admin_token):
            # 获取部门详情
            test_get_department_detail(admin_token)
            
            # 更新部门
            test_update_department(admin_token)
            
            # 再次获取部门详情，验证更新是否成功
            test_get_department_detail(admin_token)
            
            # 删除部门
            test_delete_department(admin_token)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
    finally:
        # 确保无论如何都尝试清理测试数据
        if test_dept_code:
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.delete(f"{BASE_URL}/{test_dept_code}", headers=headers)
                print(f"\n清理测试数据: {response.status_code == 200 or response.status_code == 404}")
            except:
                pass
    
    print("\n===== 部门模块API测试结束 =====")

if __name__ == "__main__":
    run_dept_api_tests()
