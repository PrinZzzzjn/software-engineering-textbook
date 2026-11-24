#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试创建人员API脚本
"""
import os
import sys
import json
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
PERSONNEL_URL = f"{BASE_URL}/personnel"

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

def test_create_personnel():
    # 首先登录获取访问令牌
    access_token = login()
    if not access_token:
        print("❌ 无法继续测试，因为未获取到有效的访问令牌")
        return
    
    # 测试数据（使用dept_code=1001）
    personnel_data = {
        "name": "张三",
        "certificate_number": "987654321",  # 使用新的工号
        "id_card_number": "112345699874453188",  # 使用新的身份证号
        "department_id": 1001,
        "position": "经理",
        "rank": "一级",
        "hire_date": "2025-11-06"
    }
    
    print("\n测试创建人员API...")
    print(f"请求数据: {personnel_data}")
    
    # 添加认证头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            PERSONNEL_URL,
            json=personnel_data,
            headers=headers
        )
        
        # 打印响应信息
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✅ 创建人员成功！")
        else:
            print("❌ 创建人员失败！")
            
    except Exception as e:
        print(f"❌ 请求出错: {str(e)}")

if __name__ == "__main__":
    test_create_personnel()