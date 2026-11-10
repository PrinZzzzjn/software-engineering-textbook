#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试创建工位API脚本
"""
import os
import sys
import json
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
WORKSTATION_URL = f"{BASE_URL}/workstation"

# 测试账号信息
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def login():
    """登录获取访问令牌"""
    print("尝试登录获取访问令牌...")
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    print(f"登录数据: {login_data}")
    
    try:
        response = requests.post(AUTH_URL, json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 登录成功，获取到访问令牌！")
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ 登录失败或未获取到访问令牌！")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {str(e)}")
        return None

def test_create_workstation():
    """测试创建工位"""
    # 首先登录获取访问令牌
    access_token = login()
    if not access_token:
        print("❌ 无法继续测试，因为未获取到有效的访问令牌")
        return
    
    print("\n准备创建工位...")
    
    # 准备创建工位的数据
    # 注意：确保JSON格式正确，特别是逗号使用
    workstation_data = {
        "workstation_id": 1002,
        "workstation_name": "测试工位2",
        "dept_code": 1000,
        "category_code": 1,
        "longitude": 116.4074,
        "latitude": 39.9042,
        "remark": "这是一个测试工位"
    }
    
    print(f"创建工位数据: {workstation_data}")
    
    # 设置请求头，包含访问令牌
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 发送创建工位请求
        response = requests.post(
            WORKSTATION_URL,
            json=workstation_data,
            headers=headers
        )
        
        print(f"\n创建工位响应状态码: {response.status_code}")
        print(f"创建工位响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✅ 工位创建成功！")
        else:
            print(f"❌ 工位创建失败，状态码: {response.status_code}")
            
            # 尝试解析错误响应
            try:
                error_data = response.json()
                print(f"错误详情: {error_data}")
                if "detail" in error_data:
                    print(f"错误描述: {error_data['detail']}")
            except json.JSONDecodeError:
                print("无法解析错误响应为JSON")
                
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
        print("请检查请求数据格式是否正确")
    except Exception as e:
        print(f"❌ 创建工位请求失败: {str(e)}")

if __name__ == "__main__":
    test_create_workstation()
