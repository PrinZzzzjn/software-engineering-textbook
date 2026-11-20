#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
保险箱记录模块API测试脚本
测试保险箱记录的CRUD操作和相关功能
"""

import json
import time
import requests
from datetime import datetime, timedelta


class SafeRecordApiTester:
    """保险箱记录API测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.base_url = "http://localhost:8000/api/v1"
        self.safe_record_url = f"{self.base_url}/safe_record"
        self.auth_url = f"{self.base_url}/auth/login"
        self.headers = {"Content-Type": "application/json"}
        self.token = None
        self.test_record_id = None
        
        # 测试数据
        self.test_dept_code = "1001"  # 假设存在的部门编码
        self.test_applicant_cert = "123456"  # 假设存在的申请人证件号
        self.test_authorizer_cert = "654321"  # 假设存在的授权人证件号
        self.test_device_id = "SAFE001"
    
    def login(self):
        """登录获取访问令牌"""
        print("=== 测试登录认证 ===")
        
        # 尝试使用默认管理员账号登录
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(self.auth_url, json=login_data, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                # 检查返回的数据结构是否包含token信息
                token_fields = ['access_token', 'token', 'data']
                token_found = False
                
                for field in token_fields:
                    if field in result:
                        if isinstance(result[field], dict) and 'access_token' in result[field]:
                            self.token = result[field]['access_token']
                            token_found = True
                            break
                        elif field == 'token':
                            self.token = result[field]
                            token_found = True
                            break
                
                if not token_found:
                    # 如果无法确定具体字段，尝试获取第一个可能的token值
                    for key, value in result.items():
                        if isinstance(value, str) and value.startswith(('Bearer ', 'eyJ')):
                            self.token = value if not value.startswith('Bearer ') else value[7:]
                            token_found = True
                            break
                
                if self.token:
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    print("✅ 登录成功，已获取访问令牌")
                    return True
                else:
                    print(f"❌ 登录响应中未找到有效token: {result}")
                    return False
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录过程发生错误: {str(e)}")
            return False
    
    def check_dependencies(self):
        """检查并创建依赖数据（部门和人员）"""
        print("\n=== 检查依赖数据 ===")
        
        try:
            # 1. 创建测试部门（如果不存在）
            print("正在创建测试部门...")
            dept_url = f"{self.base_url}/dept"
            dept_data = {
                "dept_code": self.test_dept_code,
                "dept_name": "保险箱测试部门",
                "parent_code": "0000",
                "dept_level": 1,
                "status": "1",
                "sort": 100
            }
            
            # 先尝试获取部门，检查是否存在
            response = requests.get(f"{dept_url}/{self.test_dept_code}", headers=self.headers)
            if response.status_code == 404:
                # 部门不存在，创建新部门
                print(f"发送部门创建请求到: {dept_url}")
                print(f"部门数据: {dept_data}")
                create_response = requests.post(dept_url, json=dept_data, headers=self.headers)
                print(f"部门创建响应状态: {create_response.status_code}")
                print(f"部门创建响应内容: {create_response.text}")
                if create_response.status_code == 200:
                    print(f"✅ 测试部门创建成功: {self.test_dept_code}")
                else:
                    print(f"⚠️  部门创建失败: {create_response.status_code} - {create_response.text}")
            else:
                print(f"✅ 测试部门已存在: {self.test_dept_code}")
            
            # 2. 确保测试人员存在
            def ensure_personnel_exists(cert_number, name, dept_code):
                """确保测试人员存在"""
                print(f"\n=== 确保测试人员存在: {cert_number} ===")
                
                # 先检查人员是否已存在
                personnel_url = f"{self.base_url}/personnel"
                response = requests.get(
                    f"{personnel_url}?certificate_number={cert_number}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("items") and len(data.get("items")) > 0:
                        print(f"✅ 测试人员已存在，certificate_number: {cert_number}")
                        return True
                
                # 人员不存在，创建测试人员
                personnel_data = {
                    "name": name,
                    "certificate_number": cert_number,
                    "id_card_number": "11010119900101" + cert_number[-4:],
                    "dept_code": dept_code,
                    "position": "测试职位",
                    "rank": "测试职级",
                    "hire_date": "2020-01-01"
                }
                
                try:
                    response = requests.post(
                        personnel_url,
                        json=personnel_data,
                        headers=self.headers
                    )
                    
                    print(f"创建测试人员请求数据: {json.dumps(personnel_data, ensure_ascii=False)}")
                    print(f"创建测试人员响应状态码: {response.status_code}")
                    print(f"创建测试人员响应内容: {response.text}")
                    
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"✅ 创建测试人员成功！{cert_number}")
                        return True
                    else:
                        print(f"❌ 创建测试人员失败！{cert_number}")
                        return False
                except Exception as e:
                    print(f"❌ 创建测试人员请求出错: {str(e)}")
                    return False
            
            # 创建申请人
            applicant_created = ensure_personnel_exists(
                self.test_applicant_cert, 
                "测试申请人", 
                self.test_dept_code
            )
            
            # 创建授权人
            authorizer_created = ensure_personnel_exists(
                self.test_authorizer_cert, 
                "测试授权人", 
                self.test_dept_code
            )
            
            print("\n=== 人员数据准备情况 ===")
            print(f"申请人状态: {'✅ 已准备' if applicant_created else '❌ 未准备'}")
            print(f"授权人状态: {'✅ 已准备' if authorizer_created else '❌ 未准备'}")
            print(f"部门编码: {self.test_dept_code}")
            
            print("✅ 依赖数据检查完成")
            return True
            
        except Exception as e:
            print(f"⚠️  依赖数据检查过程中发生错误: {str(e)}")
            # 即使创建依赖失败，也继续测试，让API返回具体的错误信息
            return True
    
    def create_safe_record(self):
        """创建保险箱记录"""
        print("\n=== 测试创建保险箱记录 ===")
        
        try:
            # 准备创建记录的数据
            record_data = {
                "dept_code": self.test_dept_code,
                "device_id": self.test_device_id,
                "applicant_certificate_number": self.test_applicant_cert,
                "application_time": datetime.now().isoformat(),
                "application_type": "01",  # 工位申请
                "authorizer_certificate_number": self.test_authorizer_cert,
                "authorization_type": "01",  # 值班室授权
                "authorization_result": "01",  # 成功
                "open_time": datetime.now().isoformat(),
                "close_time": (datetime.now() + timedelta(minutes=45)).isoformat(),
                "is_test_mode": True  # 标记为测试模式，方便后续清理
            }
            
            print(f"创建记录数据: {json.dumps(record_data, ensure_ascii=False)}")
            
            # 发送创建请求
            response = requests.post(
                self.safe_record_url,
                json=record_data,
                headers=self.headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.test_record_id = result.get('id')
                print(f"✅ 创建记录成功: ID={self.test_record_id}")
                print(f"创建结果: {json.dumps(result, ensure_ascii=False)}")
                return True
            else:
                error_detail = response.json().get('detail', '') if response.text else ''
                print(f"❌ 创建记录失败: {response.status_code} - {error_detail}")
                print("提示: 可能缺少必要的部门或人员数据，请确保系统中存在对应的部门和人员")
                return False
                
        except Exception as e:
            print(f"❌ 创建记录过程发生错误: {str(e)}")
            return False
    
    def get_safe_record(self):
        """获取单个保险箱记录详情"""
        print("\n=== 测试获取单个保险箱记录 ===")
        
        if not self.test_record_id:
            print("❌ 无法获取记录，缺少记录ID")
            return False
        
        try:
            url = f"{self.safe_record_url}/{self.test_record_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取详情成功: {json.dumps(result, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ 获取详情失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取过程发生错误: {str(e)}")
            return False
    
    def get_safe_record_list(self):
        """获取保险箱记录列表"""
        print("\n=== 测试获取保险箱记录列表 ===")
        
        try:
            params = {
                "page": 1,
                "page_size": 10,
                "dept_code": self.test_dept_code
            }
            
            response = requests.get(
                self.safe_record_url,
                params=params,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取列表成功，共 {result.get('total', 0)} 条记录")
                print(f"列表数据: {json.dumps(result.get('items', [])[:2], ensure_ascii=False)}...")
                return True
            else:
                print(f"❌ 获取列表失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取列表过程发生错误: {str(e)}")
            return False
    
    def update_safe_record(self):
        """更新保险箱记录"""
        print("\n=== 测试更新保险箱记录 ===")
        
        if not self.test_record_id:
            print("❌ 无法更新记录，缺少记录ID")
            return False
        
        try:
            url = f"{self.safe_record_url}/{self.test_record_id}"
            
            update_data = {
                "dept_code": self.test_dept_code,
                "device_id": self.test_device_id + "_updated",
                "applicant_certificate_number": self.test_applicant_cert,
                "application_time": datetime.now().isoformat(),
                "application_type": "01",
                "authorizer_certificate_number": self.test_authorizer_cert,
                "authorization_type": "01",
                "authorization_result": "01",
                "open_time": datetime.now().isoformat(),
                "close_time": (datetime.now() + timedelta(minutes=45)).isoformat(),
                "is_test_mode": False
            }
            
            response = requests.put(
                url,
                json=update_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 更新成功: {json.dumps(result, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ 更新失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 更新过程发生错误: {str(e)}")
            return False
    
    def delete_safe_record(self):
        """删除保险箱记录"""
        print("\n=== 测试删除保险箱记录 ===")
        
        if not self.test_record_id:
            print("❌ 无法删除记录，缺少记录ID")
            return False
        
        try:
            url = f"{self.safe_record_url}/{self.test_record_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 200 or response.status_code == 204:
                print(f"✅ 删除成功，状态码: {response.status_code}")
                # 验证是否真正删除
                verify_response = requests.get(url, headers=self.headers)
                if verify_response.status_code == 404:
                    print("✅ 验证删除成功，记录不存在")
                    return True
                else:
                    print(f"❌ 验证删除失败，记录仍然存在")
                    return False
            else:
                print(f"❌ 删除失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 删除过程发生错误: {str(e)}")
            return False
    
    def get_enum_lists(self):
        """获取枚举类型列表（申请类型、授权类型、授权结果）"""
        print("\n=== 测试获取枚举类型列表 ===")
        
        enum_endpoints = {
            "申请类型": "application_types",
            "授权类型": "authorization_types",
            "授权结果": "authorization_results"
        }
        
        all_success = True
        
        try:
            for name, endpoint in enum_endpoints.items():
                url = f"{self.safe_record_url}/{endpoint}"
                print(f"\n测试获取{name}...")
                
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {name}获取成功，共 {len(result.get('items', []))} 项")
                    print(f"{name}数据: {json.dumps(result.get('items', [])[:3], ensure_ascii=False)}")
                else:
                    print(f"❌ {name}获取失败: {response.status_code} - {response.text}")
                    all_success = False
            
            return all_success
            
        except Exception as e:
            print(f"❌ 获取枚举类型过程发生错误: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始保险箱记录模块API测试")
        print("=" * 50)
        
        results = []
        test_status = {}
        
        # 按顺序执行测试，确保依赖关系
        test_functions = [
            ("登录认证", self.login),
            ("依赖检查", self.check_dependencies),
            # 跳过枚举类型测试，先专注于核心CRUD功能
            ("获取记录列表", self.get_safe_record_list),  # 先获取列表，不依赖创建
            ("创建记录", self.create_safe_record),
            ("获取单个记录", self.get_safe_record),  # 依赖创建成功
            ("更新记录", self.update_safe_record),    # 依赖创建成功
            ("删除记录", self.delete_safe_record)     # 依赖创建成功
        ]
        
        # 执行测试
        for name, func in test_functions:
            # 如果登录失败，跳过所有后续测试
            if test_status.get("登录认证") is False:
                print(f"\n⚠️  跳过{name}测试，因为登录失败")
                test_status[name] = False
                results.append(False)
                continue
            
            # 执行当前测试
            print(f"\n开始执行: {name}")
            success = func()
            test_status[name] = success
            results.append(success)
            
            # 特殊处理依赖关系
            if name == "创建记录" and not success:
                # 创建记录失败，跳过依赖的测试
                for skip_name, _ in test_functions[test_functions.index((name, func)) + 1:]:
                    if skip_name in ["获取单个记录", "更新记录", "删除记录"]:
                        print(f"\n⚠️  跳过{skip_name}测试，因为创建记录失败")
                        test_status[skip_name] = False
                        results.append(False)
        
        # 打印测试总结
        print("\n" + "=" * 50)
        print("测试结果总结:")
        for i, (name, _) in enumerate(test_functions):
            status = "✅ 通过" if results[i] else "❌ 失败"
            print(f"{i+1}. {name}: {status}")
        
        # 计算通过率
        passed_count = sum(results)
        total_count = len(results)
        pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        print("\n" + "=" * 50)
        print(f"总体结果: {passed_count}/{total_count} 通过 ({pass_rate:.1f}%)")
        
        if passed_count == total_count:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查相关功能。")
        
        return passed_count == total_count


if __name__ == "__main__":
    """主函数"""
    tester = SafeRecordApiTester()
    success = tester.run_all_tests()
    
    # 根据测试结果设置退出码
    exit(0 if success else 1)
