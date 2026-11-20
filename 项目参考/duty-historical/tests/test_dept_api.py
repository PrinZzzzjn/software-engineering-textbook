#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部门模块API测试脚本
测试功能：新建部门、更新部门、删除部门
"""
import json
import requests

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
DEPARTMENTS_URL = f"{BASE_URL}/departments"

# 测试账号信息
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 用于存储测试数据
TEST_DEPT_CODE = 10001

class DeptApiTester:
    def __init__(self):
        self.access_token = None
        self.test_dept_id = None
    
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
    
    def test_create_department(self):
        """测试创建部门"""
        print("\n=== 测试创建部门 ===")
        
        # 首先检查部门是否已存在
        try:
            check_response = requests.get(
                f"{DEPARTMENTS_URL}?dept_code={TEST_DEPT_CODE}",
                headers=self._get_headers()
            )
            
            if check_response.status_code == 200:
                data = check_response.json()
                departments = data.get("items", [])
                if departments and len(departments) > 0:
                    print(f"✅ 测试部门已存在，dept_code: {TEST_DEPT_CODE}")
                    self.test_dept_id = departments[0].get("id")
                    return True
        except Exception as e:
            print(f"检查部门是否存在时出错: {str(e)}")
        
        # 部门不存在，创建新部门
        dept_data = {
            "dept_code": TEST_DEPT_CODE,
            "full_name": "测试部门",
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
            
            print(f"创建部门响应内容: {response.text}")
            
            if response.status_code in [200, 201]:  # 接受200或201作为成功状态码
                print("✅ 创建部门成功！")
                return True
            else:
                # 如果是部门名称已存在（409错误），尝试使用不同的部门名称
                if response.status_code == 409:
                    print("🔄 尝试使用不同的部门名称创建...")
                    import time
                    timestamp = int(time.time())
                    dept_data["full_name"] = f"测试部门-{timestamp}"
                    
                    retry_response = requests.post(
                        DEPARTMENTS_URL,
                        json=dept_data,
                        headers=self._get_headers()
                    )
                    
                    print(f"重试创建部门响应内容: {retry_response.text}")
                    
                    if retry_response.status_code in [200, 201]:
                        print("✅ 重试创建部门成功！")
                        return True
                
                print(f"❌ 创建部门失败！")
                return False
                
        except Exception as e:
            print(f"❌ 创建部门请求出错: {str(e)}")
            return False
    
    def test_update_department(self):
        """测试更新部门"""
        print("\n=== 测试更新部门 ===")
        
        update_data = {
            "full_name": "测试部门-已更新",
            "address": "测试地址-已更新"
        }
        
        try:
            # 优先使用缓存的部门ID
            dept_id = self.test_dept_id
            
            # 如果没有缓存的部门ID，通过API查询获取
            if not dept_id:
                response = requests.get(
                    f"{DEPARTMENTS_URL}?dept_code={TEST_DEPT_CODE}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    departments = data.get("items", [])
                    if departments and len(departments) > 0:
                        test_dept = departments[0]
                        dept_id = test_dept.get("id")
                        self.test_dept_id = dept_id
                    else:
                        print(f"❌ 未找到测试部门，dept_code: {TEST_DEPT_CODE}")
                        return False
                else:
                    print(f"❌ 获取部门列表失败，状态码: {response.status_code}")
                    return False
            
            if dept_id:
                # 执行更新操作
                update_url = f"{DEPARTMENTS_URL}/{dept_id}"
                update_response = requests.put(
                    update_url,
                    json=update_data,
                    headers=self._get_headers()
                )
                
                print(f"更新部门响应状态码: {update_response.status_code}")
                print(f"更新部门响应内容: {update_response.text}")
                
                if update_response.status_code in [200, 201]:
                    print("✅ 更新部门成功！")
                    return True
                else:
                    print(f"❌ 更新部门失败！")
                    return False
            else:
                print(f"❌ 未找到有效的部门ID")
                return False
                
        except Exception as e:
            print(f"❌ 更新部门请求出错: {str(e)}")
            return False
    
    def test_delete_department(self):
        """测试删除部门"""
        print("\n=== 测试删除部门 ===")
        
        try:
            # 优先使用缓存的部门ID
            dept_id = self.test_dept_id
            
            # 如果没有缓存的部门ID，通过API查询获取
            if not dept_id:
                response = requests.get(
                    f"{DEPARTMENTS_URL}?dept_code={TEST_DEPT_CODE}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    departments = data.get("items", [])
                    if departments and len(departments) > 0:
                        test_dept = departments[0]
                        dept_id = test_dept.get("id")
                        self.test_dept_id = dept_id
                    else:
                        print(f"❌ 未找到测试部门，dept_code: {TEST_DEPT_CODE}")
                        return False
                else:
                    print(f"❌ 获取部门列表失败，状态码: {response.status_code}")
                    return False
            
            if dept_id:
                # 执行删除操作
                delete_url = f"{DEPARTMENTS_URL}/{dept_id}"
                delete_response = requests.delete(
                    delete_url,
                    headers=self._get_headers()
                )
                
                print(f"删除部门响应状态码: {delete_response.status_code}")
                print(f"删除部门响应内容: {delete_response.text}")
                
                if delete_response.status_code in [200, 201]:
                    print("✅ 删除部门成功！")
                    return True
                else:
                    print(f"❌ 删除部门失败！")
                    return False
            else:
                print(f"❌ 未找到有效的部门ID")
                return False
                
        except Exception as e:
            print(f"❌ 删除部门请求出错: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行部门模块API测试...")
        
        # 1. 登录
        if not self.login():
            print("测试终止：无法登录")
            return
        
        create_success = False
        update_success = False
        delete_success = False
        
        try:
            # 2. 创建部门
            create_success = self.test_create_department()
            
            # 3. 更新部门（只有创建成功才进行）
            if create_success:
                update_success = self.test_update_department()
            
            # 4. 删除部门（只有创建成功才进行清理）
            if create_success:
                delete_success = self.test_delete_department()
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {str(e)}")
        finally:
            # 确保即使出错也清理测试数据
            if self.test_dept_id:
                try:
                    # 尝试删除测试部门
                    delete_url = f"{DEPARTMENTS_URL}/{self.test_dept_id}"
                    requests.delete(
                        delete_url,
                        headers=self._get_headers()
                    )
                    print("\n🗑️  测试数据清理完成")
                except:
                    pass
        
        # 输出测试结果摘要
        print("\n=== 测试结果摘要 ===")
        print(f"登录: {'✅ 成功' if self.access_token else '❌ 失败'}")
        print(f"创建部门: {'✅ 成功' if create_success else '❌ 失败'}")
        print(f"更新部门: {'✅ 成功' if update_success else '❌ 失败'}")
        print(f"删除部门: {'✅ 成功' if delete_success else '❌ 失败'}")
        print("\n测试完成！")

if __name__ == "__main__":
    tester = DeptApiTester()
    tester.run_all_tests()
