#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
值班记录模块API测试脚本
测试功能：创建值班记录、获取值班记录列表、获取单个值班记录、更新值班记录、删除值班记录
"""
import json
import requests
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
DUTY_RECORD_URL = f"{BASE_URL}/duty-records"
PERSONNEL_URL = f"{BASE_URL}/personnel"
WORKSTATION_URL = f"{BASE_URL}/workstation"

# 测试账号信息（使用管理员账号，因为创建、更新、删除需要管理员权限）
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 用于存储测试数据
TEST_PERSONNEL_CERT_NUMBER = "TEST001"
TEST_SUCCESSOR_CERT_NUMBER = "TEST002"
TEST_WORKSTATION_ID = "WS001"
TEST_DUTY_RECORD_ID = None

class DutyRecordApiTester:
    def __init__(self):
        self.access_token = None
        self.test_duty_record_id = None
    
    def login(self):
        """用户登录获取访问令牌"""
        print("\n=== 测试登录认证 ===")
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        try:
            print(f"尝试登录，URL: {LOGIN_URL}")
            print(f"登录数据: {json.dumps(login_data)}")
            
            response = requests.post(
                LOGIN_URL,
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"登录响应状态码: {response.status_code}")
            print(f"登录响应内容: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"登录响应JSON: {json.dumps(data, ensure_ascii=False)}")
                    
                    # 检查不同可能的token字段名
                    possible_token_fields = ["access_token", "token", "jwt", "bearer_token"]
                    for field in possible_token_fields:
                        if field in data:
                            self.access_token = data[field]
                            print(f"✅ 登录成功，从字段 '{field}' 获取到访问令牌！")
                            return True
                    
                    print(f"❌ 登录响应中未找到预期的令牌字段！")
                    return False
                    
                except json.JSONDecodeError:
                    print(f"❌ 登录响应不是有效的JSON格式！")
                    return False
            else:
                print(f"❌ 登录请求失败，状态码: {response.status_code}")
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
    
    def ensure_personnel_exists(self, cert_number, name):
        """确保测试人员存在"""
        print(f"\n=== 确保测试人员存在: {cert_number} ===")
        
        # 先检查人员是否已存在
        response = requests.get(
            f"{PERSONNEL_URL}?certificate_number={cert_number}",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("items") and len(data.get("items")) > 0:
                print(f"✅ 测试人员已存在，certificate_number: {cert_number}")
                return True
        
        # 人员不存在，创建测试人员
        # 先确保有可用的部门
        dept_response = requests.get(
            f"{BASE_URL}/departments",
            headers=self._get_headers()
        )
        
        if dept_response.status_code != 200 or not dept_response.json().get("items"):
            print("❌ 无法获取部门信息，需要先创建部门")
            # 创建一个测试部门
            dept_data = {
                "dept_code": 10001,
                "full_name": "测试部门",
                "address": "测试地址",
                "longitude": 116.3974,
                "latitude": 39.9093,
                "parent_dept_code": None
            }
            create_dept_response = requests.post(
                f"{BASE_URL}/departments",
                json=dept_data,
                headers=self._get_headers()
            )
            
            if create_dept_response.status_code != 200:
                print(f"❌ 创建测试部门失败！")
                return False
            
            dept_code = 10001
        else:
            # 使用第一个部门
            dept_code = dept_response.json().get("items")[0].get("dept_code")
        
        # 创建测试人员
        personnel_data = {
            "name": name,
            "certificate_number": cert_number,
            "id_card_number": "110101199001011234",
            "dept_code": dept_code,
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
            
            print(f"创建测试人员响应状态码: {response.status_code}")
            print(f"创建测试人员响应内容: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ 创建测试人员成功！{cert_number}")
                return True
            else:
                print(f"❌ 创建测试人员失败！{cert_number}")
                return False
                
        except Exception as e:
            print(f"❌ 创建测试人员请求出错: {str(e)}")
            return False
    
    def ensure_workstation_exists(self):
        """确保测试工位存在"""
        print(f"\n=== 确保测试工位存在: {TEST_WORKSTATION_ID} ===")
        
        # 先检查工位是否已存在
        response = requests.get(
            f"{WORKSTATION_URL}?workstation_id={TEST_WORKSTATION_ID}",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("items") and len(data.get("items")) > 0:
                print(f"✅ 测试工位已存在，workstation_id: {TEST_WORKSTATION_ID}")
                return True
        
        # 工位不存在，创建测试工位
        workstation_data = {
            "workstation_id": TEST_WORKSTATION_ID,
            "name": "测试工位",
            "location": "测试位置",
            "description": "测试工位描述",
            "status": "normal"
        }
        
        try:
            response = requests.post(
                WORKSTATION_URL,
                json=workstation_data,
                headers=self._get_headers()
            )
            
            print(f"创建测试工位响应状态码: {response.status_code}")
            print(f"创建测试工位响应内容: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ 创建测试工位成功！")
                return True
            else:
                print(f"❌ 创建测试工位失败！")
                return False
                
        except Exception as e:
            print(f"❌ 创建测试工位请求出错: {str(e)}")
            return False
    
    def test_create_duty_record(self):
        """测试创建值班记录"""
        print("\n=== 测试创建值班记录 ===")
        
        # 尝试使用已存在的数据，而不是创建新数据
        # 从测试结果看到系统中已有数据，我们使用这些数据
        existing_personnel_cert = "ZHANG001"  # 张三
        existing_workstation_id = "WS001"  # 测试工位1
        
        # 计算值班时间（当前时间往前1天到当前时间）
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        # 格式化时间为YYYY-MM-DD HH:MM:SS格式
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        
        duty_record_data = {
            "personnel_certificate_number": existing_personnel_cert,
            "workstation_id": existing_workstation_id,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "status": "normal",
            "remark": "测试值班记录 - 修复版"
        }
        
        print(f"创建值班记录数据: {json.dumps(duty_record_data, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                DUTY_RECORD_URL,
                json=duty_record_data,
                headers=self._get_headers()
            )
            
            print(f"创建值班记录响应状态码: {response.status_code}")
            print(f"创建值班记录响应内容: {response.text}")
            
            if response.status_code == 201:
                data = response.json()
                self.test_duty_record_id = data.get("id")
                print(f"✅ 创建值班记录成功！ID: {self.test_duty_record_id}")
                return True
            else:
                print(f"❌ 创建值班记录失败！")
                return False
                
        except Exception as e:
            print(f"❌ 创建值班记录请求出错: {str(e)}")
            return False
    
    def test_get_duty_record(self):
        """测试获取单个值班记录"""
        print("\n=== 测试获取单个值班记录 ===")
        
        if not self.test_duty_record_id:
            # 如果没有记录ID，先查找测试记录
            print("查找测试值班记录...")
            response = requests.get(
                f"{DUTY_RECORD_URL}?personnel_certificate_number={TEST_PERSONNEL_CERT_NUMBER}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    self.test_duty_record_id = items[0].get("id")
                    print(f"找到测试值班记录，ID: {self.test_duty_record_id}")
                else:
                    print("❌ 未找到测试值班记录")
                    return False
            else:
                print(f"❌ 获取值班记录列表失败")
                return False
        
        try:
            response = requests.get(
                f"{DUTY_RECORD_URL}/{self.test_duty_record_id}",
                headers=self._get_headers()
            )
            
            print(f"获取单个值班记录响应状态码: {response.status_code}")
            print(f"获取单个值班记录响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 获取单个值班记录成功！")
                return True
            else:
                print(f"❌ 获取单个值班记录失败！")
                return False
                
        except Exception as e:
            print(f"❌ 获取单个值班记录请求出错: {str(e)}")
            return False
    
    def test_get_duty_record_list(self):
        """测试获取值班记录列表"""
        print("\n=== 测试获取值班记录列表 ===")
        
        try:
            response = requests.get(
                f"{DUTY_RECORD_URL}?page=1&page_size=10",
                headers=self._get_headers()
            )
            
            print(f"获取值班记录列表响应状态码: {response.status_code}")
            print(f"获取值班记录列表响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 获取值班记录列表成功！")
                return True
            else:
                print(f"❌ 获取值班记录列表失败！")
                return False
                
        except Exception as e:
            print(f"❌ 获取值班记录列表请求出错: {str(e)}")
            return False
    
    def test_update_duty_record(self):
        """测试更新值班记录"""
        print("\n=== 测试更新值班记录 ===")
        
        if not self.test_duty_record_id:
            # 如果没有记录ID，先查找测试记录
            response = requests.get(
                f"{DUTY_RECORD_URL}?personnel_certificate_number={TEST_PERSONNEL_CERT_NUMBER}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    self.test_duty_record_id = items[0].get("id")
                else:
                    print("❌ 未找到测试值班记录")
                    return False
            else:
                print(f"❌ 获取值班记录列表失败")
                return False
        
        update_data = {
            "status": "completed",
            "remark": "测试值班记录-已更新"
        }
        
        try:
            response = requests.put(
                f"{DUTY_RECORD_URL}/{self.test_duty_record_id}",
                json=update_data,
                headers=self._get_headers()
            )
            
            print(f"更新值班记录响应状态码: {response.status_code}")
            print(f"更新值班记录响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 更新值班记录成功！")
                return True
            else:
                print(f"❌ 更新值班记录失败！")
                return False
                
        except Exception as e:
            print(f"❌ 更新值班记录请求出错: {str(e)}")
            return False
    
    def test_delete_duty_record(self):
        """测试删除值班记录"""
        print("\n=== 测试删除值班记录 ===")
        
        if not self.test_duty_record_id:
            # 如果没有记录ID，先查找测试记录
            response = requests.get(
                f"{DUTY_RECORD_URL}?personnel_certificate_number={TEST_PERSONNEL_CERT_NUMBER}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    self.test_duty_record_id = items[0].get("id")
                else:
                    print("❌ 未找到测试值班记录")
                    return False
            else:
                print(f"❌ 获取值班记录列表失败")
                return False
        
        try:
            response = requests.delete(
                f"{DUTY_RECORD_URL}/{self.test_duty_record_id}",
                headers=self._get_headers()
            )
            
            print(f"删除值班记录响应状态码: {response.status_code}")
            print(f"删除值班记录响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 删除值班记录成功！")
                return True
            else:
                print(f"❌ 删除值班记录失败！")
                return False
                
        except Exception as e:
            print(f"❌ 删除值班记录请求出错: {str(e)}")
            return False
    
    def test_duty_statistics(self):
        """测试获取值班统计信息"""
        print("\n=== 测试获取值班统计信息 ===")
        
        # 计算时间范围（过去30天）
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        try:
            response = requests.get(
                f"{DUTY_RECORD_URL}/statistics/summary?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}",
                headers=self._get_headers()
            )
            
            print(f"获取值班统计信息响应状态码: {response.status_code}")
            print(f"获取值班统计信息响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 获取值班统计信息成功！")
                return True
            else:
                print(f"❌ 获取值班统计信息失败！")
                return False
                
        except Exception as e:
            print(f"❌ 获取值班统计信息请求出错: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行值班记录模块API测试...")
        
        # 1. 登录
        login_success = self.login()
        
        # 2. 获取值班记录列表（不需要创建也可以测试）
        get_list_success = False
        if login_success:
            get_list_success = self.test_get_duty_record_list()
        
        # 3. 获取值班统计信息（不需要创建也可以测试）
        statistics_success = False
        if login_success:
            statistics_success = self.test_duty_statistics()
        
        # 4. 创建值班记录
        create_success = False
        if login_success:
            create_success = self.test_create_duty_record()
        
        # 5. 获取单个值班记录
        get_single_success = False
        if create_success:
            get_single_success = self.test_get_duty_record()
        
        # 6. 更新值班记录
        update_success = False
        if create_success:
            update_success = self.test_update_duty_record()
        
        # 7. 删除值班记录（清理测试数据）
        delete_success = False
        if create_success:
            delete_success = self.test_delete_duty_record()
        
        # 输出测试结果摘要
        print("\n=== 测试结果摘要 ===")
        print(f"登录: {'✅ 成功' if login_success else '❌ 失败'}")
        print(f"获取值班记录列表: {'✅ 成功' if get_list_success else '❌ 失败'}")
        print(f"获取值班统计信息: {'✅ 成功' if statistics_success else '❌ 失败'}")
        print(f"创建值班记录: {'✅ 成功' if create_success else '❌ 失败'}")
        print(f"获取单个值班记录: {'✅ 成功' if get_single_success else '❌ 失败'}")
        print(f"更新值班记录: {'✅ 成功' if update_success else '❌ 失败'}")
        print(f"删除值班记录: {'✅ 成功' if delete_success else '❌ 失败'}")
        
        # 计算总体成功率
        total_tests = 7
        passed_tests = sum([1 for success in [login_success, get_list_success, statistics_success, 
                                           create_success, get_single_success, update_success, delete_success] 
                          if success])
        
        print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")
        print("测试完成！")

if __name__ == "__main__":
    tester = DutyRecordApiTester()
    tester.run_all_tests()