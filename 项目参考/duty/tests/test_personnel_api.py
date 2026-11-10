#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人员模块API测试脚本
测试功能：新建人员、更新人员、删除人员
"""
import json
import requests
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
PERSONNEL_URL = f"{BASE_URL}/personnel"
DEPARTMENTS_URL = f"{BASE_URL}/departments"

# 测试账号信息
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 用于存储测试数据
TEST_CERTIFICATE_NUMBER = "TEST001"
TEST_DEPT_CODE = 10001  # 确保此部门编码存在

class PersonnelApiTester:
    def __init__(self):
        self.access_token = None
        self.test_personnel_id = None
    
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
            "full_name": "测试部门-人员测试用",
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
    
    def test_create_personnel(self):
        """测试创建人员"""
        print("\n=== 测试创建人员 ===")
        
        # 确保测试部门存在
        if not self.ensure_department_exists():
            return False
        
        personnel_data = {
            "name": "测试人员",
            "certificate_number": TEST_CERTIFICATE_NUMBER,
            "id_card_number": "110101199001011234",
            "dept_code": TEST_DEPT_CODE,
            "position": "测试职位",
            "rank": "测试职级",
            "hire_date": "2020-01-01"
        }
        
        try:
            response = requests.post(
                PERSONNEL_URL,
                json=personnel_data,
                headers=self._get_headers()
            )
            
            print(f"创建人员响应状态码: {response.status_code}")
            print(f"创建人员响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.test_personnel_id = data.get("id")
                print("✅ 创建人员成功！")
                return True
            else:
                print(f"❌ 创建人员失败！")
                return False
                
        except Exception as e:
            print(f"❌ 创建人员请求出错: {str(e)}")
            return False
    
    def test_update_personnel(self):
        """测试更新人员"""
        print("\n=== 测试更新人员 ===")
        
        update_data = {
            "name": "测试人员-已更新",
            "position": "测试职位-已更新"
        }
        
        try:
            # 先获取人员列表找到测试人员的ID
            response = requests.get(
                f"{PERSONNEL_URL}?certificate_number={TEST_CERTIFICATE_NUMBER}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                personnels = data.get("items", [])
                test_person = next((p for p in personnels if p.get("certificate_number") == TEST_CERTIFICATE_NUMBER), None)
                
                if test_person:
                    personnel_id = test_person.get("id")
                    update_url = f"{PERSONNEL_URL}/{personnel_id}"
                    
                    # 执行更新操作
                    update_response = requests.put(
                        update_url,
                        json=update_data,
                        headers=self._get_headers()
                    )
                    
                    print(f"更新人员响应状态码: {update_response.status_code}")
                    print(f"更新人员响应内容: {update_response.text}")
                    
                    if update_response.status_code == 200:
                        print("✅ 更新人员成功！")
                        return True
                    else:
                        print(f"❌ 更新人员失败！")
                        return False
                else:
                    print(f"❌ 未找到测试人员，certificate_number: {TEST_CERTIFICATE_NUMBER}")
                    return False
            else:
                print(f"❌ 获取人员列表失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 更新人员请求出错: {str(e)}")
            return False
    
    def test_delete_personnel(self):
        """测试删除人员"""
        print("\n=== 测试删除人员 ===")
        
        try:
            # 先获取人员列表找到测试人员的ID
            response = requests.get(
                f"{PERSONNEL_URL}?certificate_number={TEST_CERTIFICATE_NUMBER}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                personnels = data.get("items", [])
                test_person = next((p for p in personnels if p.get("certificate_number") == TEST_CERTIFICATE_NUMBER), None)
                
                if test_person:
                    personnel_id = test_person.get("id")
                    delete_url = f"{PERSONNEL_URL}/{personnel_id}"
                    
                    # 执行删除操作
                    delete_response = requests.delete(
                        delete_url,
                        headers=self._get_headers()
                    )
                    
                    print(f"删除人员响应状态码: {delete_response.status_code}")
                    print(f"删除人员响应内容: {delete_response.text}")
                    
                    if delete_response.status_code == 200:
                        print("✅ 删除人员成功！")
                        return True
                    else:
                        print(f"❌ 删除人员失败！")
                        return False
                else:
                    print(f"❌ 未找到测试人员，certificate_number: {TEST_CERTIFICATE_NUMBER}")
                    return False
            else:
                print(f"❌ 获取人员列表失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 删除人员请求出错: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行人员模块API测试...")
        
        # 1. 登录
        if not self.login():
            print("测试终止：无法登录")
            return
        
        # 2. 创建人员
        create_success = self.test_create_personnel()
        
        # 3. 更新人员（只有创建成功才进行）
        update_success = False
        if create_success:
            update_success = self.test_update_personnel()
        
        # 4. 删除人员（只有创建成功才进行清理）
        if create_success:
            self.test_delete_personnel()
        
        # 输出测试结果摘要
        print("\n=== 测试结果摘要 ===")
        print(f"登录: {'✅ 成功' if self.access_token else '❌ 失败'}")
        print(f"创建人员: {'✅ 成功' if create_success else '❌ 失败'}")
        print(f"更新人员: {'✅ 成功' if update_success else '❌ 失败'}")
        print("\n测试完成！")

if __name__ == "__main__":
    tester = PersonnelApiTester()
    tester.run_all_tests()
