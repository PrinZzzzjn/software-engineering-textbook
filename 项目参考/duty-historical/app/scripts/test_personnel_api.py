import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"
# 登录URL
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
# 人员API URL
PERSONNEL_LIST_URL = f"{BASE_URL}/api/v1/personnel"
PERSONNEL_DETAIL_URL = f"{BASE_URL}/api/v1/personnel/ZHANG001"

def login():
    """
    登录获取访问令牌
    """
    print("正在登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        # 解析响应，提取访问令牌
        data = response.json()
        if "access_token" in data:
            print("登录成功！")
            return data["access_token"]
        else:
            print("登录失败：未返回访问令牌")
            return None
    except Exception as e:
        print(f"登录请求异常: {str(e)}")
        return None

def test_get_personnel_list(token):
    """
    测试获取人员列表接口
    """
    print("\n测试获取人员列表接口...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(PERSONNEL_LIST_URL, headers=headers)
        print(f"获取人员列表响应状态码: {response.status_code}")
        print(f"获取人员列表响应内容: {response.text}")
        
        if response.status_code == 200:
            print("获取人员列表成功！")
            # 解析响应内容
            data = response.json()
            print(f"总记录数: {data.get('total')}")
            print(f"当前页码: {data.get('page')}")
            print(f"每页数量: {data.get('page_size')}")
            print(f"总页数: {data.get('pages')}")
            print(f"返回的人员数量: {len(data.get('items', []))}")
            return True
        else:
            print("获取人员列表失败！")
            return False
    except Exception as e:
        print(f"获取人员列表请求异常: {str(e)}")
        return False

def test_get_personnel_detail(token):
    """
    测试获取指定人员信息接口
    """
    print("\n测试获取指定人员信息接口...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(PERSONNEL_DETAIL_URL, headers=headers)
        print(f"获取指定人员信息响应状态码: {response.status_code}")
        print(f"获取指定人员信息响应内容: {response.text}")
        
        if response.status_code == 200:
            print("获取指定人员信息成功！")
            # 解析响应内容
            data = response.json()
            print(f"人员姓名: {data.get('name')}")
            print(f"工号: {data.get('certificate_number')}")
            print(f"部门编码: {data.get('dept_code')}")
            print(f"部门名称: {data.get('department_name')}")
            return True
        else:
            print("获取指定人员信息失败！")
            return False
    except Exception as e:
        print(f"获取指定人员信息请求异常: {str(e)}")
        return False

def main():
    """
    主测试函数
    """
    print("开始测试人员模块API...")
    
    # 1. 登录获取令牌
    token = login()
    if not token:
        print("无法获取访问令牌，测试终止。")
        return
    
    print(f"获取到的访问令牌: {token[:20]}...")
    
    # 2. 测试获取人员列表
    list_success = test_get_personnel_list(token)
    
    # 3. 测试获取指定人员信息
    detail_success = test_get_personnel_detail(token)
    
    # 4. 总结测试结果
    print("\n=== 测试结果总结 ===")
    print(f"获取人员列表: {'成功' if list_success else '失败'}")
    print(f"获取指定人员信息: {'成功' if detail_success else '失败'}")
    
    if list_success and detail_success:
        print("\n✅ 所有测试通过！人员模块API已修复。")
    else:
        print("\n❌ 测试未全部通过，请检查问题。")

if __name__ == "__main__":
    main()