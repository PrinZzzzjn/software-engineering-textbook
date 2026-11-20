#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工位模块API测试脚本
测试功能：新建工位、更新工位、删除工位
"""
import json
import requests

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
WORKSTATION_URL = f"{BASE_URL}/workstation"
DEPARTMENTS_URL = f"{BASE_URL}/departments"

# 测试账号信息
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 用于存储测试数据
TEST_WORKSTATION_ID = 20001
TEST_DEPT_CODE = 10001  # 确保此部门编码存在

class WorkstationApiTester:
    def __init__(self):
        self.access_token = None
        self.test_workstation_id = None
    
    def login(self):
        """用户登录获取访问令牌"""
        print("尝试登录获取访问令牌...")
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
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
                self.access_token = data.get("access_token")
                if self.access_token:
                    print("✅ 登录成功，获取到访问令牌！")
                    return True
            
            print("❌ 登录失败或未获取到访问令牌！")
            return False
            
        except Exception as e:
            print(f"❌ 登录请求出错: {str(e)}")
            return False
    
    def _get_headers(self):
        """获取请求头，包含访问令牌"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
    
    def ensure_department_exists(self):
        """确保测试部门存在"""
        print("\n=== 确保测试部门存在 ===")
        
        # 先检查部门是否已存在
        response = requests.get(
            f"{DEPARTMENTS_URL}?dept_code={TEST_DEPT_CODE}",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("items") and len(data.get("items")) > 0:
                print(f"✅ 测试部门已存在，dept_code: {TEST_DEPT_CODE}")
                return True
        
        # 部门不存在，创建一个测试部门
        dept_data = {
            "dept_code": TEST_DEPT_CODE,
            "full_name": "测试部门-工位测试用",
            "address": "测试地址",
            "longitude": 116.3974,
            "latitude": 39.9093,
            "parent_dept_code": None
        }
        
        try:
            response = requests.post(
                DEPARTMENTS_URL,
                json=dept_data,
                headers=self._get_headers()
            )
            
            print(f"创建测试部门响应状态码: {response.status_code}")
            print(f"创建测试部门响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 创建测试部门成功！")
                return True
            else:
                print(f"❌ 创建测试部门失败！")
                return False
                
        except Exception as e:
            print(f"❌ 创建测试部门请求出错: {str(e)}")
            return False
    
    def test_create_workstation(self):
        """测试创建工位"""
        print("\n=== 测试创建工位 ===")
        
        # 确保测试部门存在
        if not self.ensure_department_exists():
            return False
        
        workstation_data = {
            "workstation_id": TEST_WORKSTATION_ID,
            "workstation_name": "测试工位",
            "dept_code": TEST_DEPT_CODE,
            "category_code": 1,
            "longitude": 116.3974,
            "latitude": 39.9093,
            "remark": "测试工位备注"
        }
        
        try:
            response = requests.post(
                WORKSTATION_URL,
                json=workstation_data,
                headers=self._get_headers()
            )
            
            print(f"创建工位响应状态码: {response.status_code}")
            print(f"创建工位响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.test_workstation_id = data.get("id")
                print("✅ 创建工位成功！")
                return True
            else:
                print(f"❌ 创建工位失败！")
                return False
                
        except Exception as e:
            print(f"❌ 创建工位请求出错: {str(e)}")
            return False
    
    def test_update_workstation(self):
        """测试更新工位"""
        print("\n=== 测试更新工位 ===")
        
        update_data = {
            "workstation_name": "测试工位-已更新",
            "remark": "测试工位备注-已更新"
        }
        
        try:
            # 先获取工位列表找到测试工位的ID
            response = requests.get(
                f"{WORKSTATION_URL}?workstation_id={TEST_WORKSTATION_ID}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                workstations = data.get("items", [])
                test_workstation = next((w for w in workstations if w.get("workstation_id") == TEST_WORKSTATION_ID), None)
                
                if test_workstation:
                    workstation_id = test_workstation.get("id")
                    update_url = f"{WORKSTATION_URL}/{workstation_id}"
                    
                    # 执行更新操作
                    update_response = requests.put(
                        update_url,
                        json=update_data,
                        headers=self._get_headers()
                    )
                    
                    print(f"更新工位响应状态码: {update_response.status_code}")
                    print(f"更新工位响应内容: {update_response.text}")
                    
                    if update_response.status_code == 200:
                        print("✅ 更新工位成功！")
                        return True
                    else:
                        print(f"❌ 更新工位失败！")
                        return False
                else:
                    print(f"❌ 未找到测试工位，workstation_id: {TEST_WORKSTATION_ID}")
                    return False
            else:
                print(f"❌ 获取工位列表失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 更新工位请求出错: {str(e)}")
            return False
    
    def test_delete_workstation(self):
        """测试删除工位"""
        print("\n=== 测试删除工位 ===")
        
        try:
            # 先获取工位列表找到测试工位的ID
            response = requests.get(
                f"{WORKSTATION_URL}?workstation_id={TEST_WORKSTATION_ID}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                workstations = data.get("items", [])
                test_workstation = next((w for w in workstations if w.get("workstation_id") == TEST_WORKSTATION_ID), None)
                
                if test_workstation:
                    workstation_id = test_workstation.get("id")
                    delete_url = f"{WORKSTATION_URL}/{workstation_id}"
                    
                    # 执行删除操作
                    delete_response = requests.delete(
                        delete_url,
                        headers=self._get_headers()
                    )
                    
                    print(f"删除工位响应状态码: {delete_response.status_code}")
                    print(f"删除工位响应内容: {delete_response.text}")
                    
                    if delete_response.status_code == 200:
                        print("✅ 删除工位成功！")
                        return True
                    else:
                        print(f"❌ 删除工位失败！")
                        return False
                else:
                    print(f"❌ 未找到测试工位，workstation_id: {TEST_WORKSTATION_ID}")
                    return False
            else:
                print(f"❌ 获取工位列表失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 删除工位请求出错: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行工位模块API测试...")
        
        # 1. 登录
        if not self.login():
            print("测试终止：无法登录")
            return
        
        # 2. 创建工位
        create_success = self.test_create_workstation()
        
        # 3. 更新工位（只有创建成功才进行）
        update_success = False
        if create_success:
            update_success = self.test_update_workstation()
        
        # 4. 删除工位（只有创建成功才进行清理）
        if create_success:
            self.test_delete_workstation()
        
        # 输出测试结果摘要
        print("\n=== 测试结果摘要 ===")
        print(f"登录: {'✅ 成功' if self.access_token else '❌ 失败'}")
        print(f"创建工位: {'✅ 成功' if create_success else '❌ 失败'}")
        print(f"更新工位: {'✅ 成功' if update_success else '❌ 失败'}")
        print("\n测试完成！")

if __name__ == "__main__":
    tester = WorkstationApiTester()
    tester.run_all_tests()
