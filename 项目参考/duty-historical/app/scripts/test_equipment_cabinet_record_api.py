import requests
import json
import datetime
import time

# API基础配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
EQUIPMENT_CABINET_RECORD_URL = f"{BASE_URL}/api/v1/equipment-cabinet-records"
PERSONNEL_URL = f"{BASE_URL}/api/v1/personnel"
DEPT_URL = f"{BASE_URL}/api/v1/departments"

# 测试账号信息
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 测试数据常量
TEST_DEPT_CODE = "TEST_DEP001"
TEST_APP_CERT_NUMBER = "PER001"
TEST_AUTH_CERT_NUMBER = "PER002"
TEST_DEVICE_ID = "DEV123456"


class EquipmentCabinetRecordApiTester:
    """设备柜记录API测试类"""
    
    def __init__(self):
        """初始化测试器"""
        self.access_token = None
        self.test_record_id = None
        self.headers = None
    
    def login(self):
        """登录并获取访问令牌"""
        print("\n=== 登录认证 ===")
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        try:
            response = requests.post(LOGIN_URL, json=login_data)
            print(f"登录响应状态码: {response.status_code}")
            print(f"登录响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.access_token}"
                    }
                    print("✅ 登录成功，已获取访问令牌")
                    return True
                else:
                    print("❌ 登录失败：未返回访问令牌")
                    return False
            else:
                print(f"❌ 登录失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录请求异常: {str(e)}")
            return False
    
    def ensure_personnel_exists(self, cert_number, name, dept_code):
        """确保测试人员存在"""
        print(f"\n=== 确保测试人员存在: {cert_number} ===")
        
        # 先检查人员是否已存在
        response = requests.get(
            f"{PERSONNEL_URL}?certificate_number={cert_number}",
            headers=self.headers
        )
        
        print(f"人员查询响应状态码: {response.status_code}")
        print(f"人员查询响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"人员查询响应数据: {json.dumps(data, ensure_ascii=False)}")
            if data.get("items"):
                print(f"找到 {len(data.get('items'))} 条人员记录")
                if len(data.get("items")) > 0:
                    print(f"✅ 测试人员已存在，certificate_number: {cert_number}")
                    return True
            else:
                print("❌ 人员查询返回空items列表")
        
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
                PERSONNEL_URL,
                json=personnel_data,
                headers=self.headers
            )
            
            print(f"创建测试人员响应状态码: {response.status_code}")
            print(f"创建测试人员响应内容: {response.text}")
            
            if response.status_code in [200, 201]:
                print(f"✅ 创建测试人员成功！{cert_number}")
                return True
            else:
                print(f"❌ 创建测试人员失败！{cert_number}")
                return False
                
        except Exception as e:
            print(f"❌ 创建测试人员请求出错: {str(e)}")
            return False
    
    def check_dependencies(self):
        """检查并创建依赖数据（部门和人员）"""
        print("\n=== 检查依赖数据 ===")
        
        try:
            # 1. 检查并创建测试部门（如果不存在）
            print("正在检查测试部门...")
            
            # 先尝试获取部门，检查是否存在
            response = requests.get(f"{DEPT_URL}/{TEST_DEPT_CODE}", headers=self.headers)
            if response.status_code == 404:
                # 部门不存在，创建新部门
                print(f"部门不存在，准备创建: {TEST_DEPT_CODE}")
                dept_data = {
                    "dept_code": TEST_DEPT_CODE,
                    "full_name": "设备柜测试部门",
                    "address": "测试地址",
                    "longitude": 116.3974,
                    "latitude": 39.9093,
                    "parent_dept_code": None
                }
                create_response = requests.post(DEPT_URL, json=dept_data, headers=self.headers)
                print(f"部门创建响应状态: {create_response.status_code}")
                print(f"部门创建响应内容: {create_response.text}")
                if create_response.status_code in [200, 201]:
                    print(f"✅ 测试部门创建成功: {TEST_DEPT_CODE}")
                else:
                    print(f"⚠️  部门创建失败: {create_response.status_code} - {create_response.text}")
                    return False
            else:
                print(f"✅ 测试部门已存在: {TEST_DEPT_CODE}")
            
            # 2. 创建测试人员（申请人和授权人）
            applicant_created = self.ensure_personnel_exists(TEST_APP_CERT_NUMBER, "测试申请人", TEST_DEPT_CODE)
            authorizer_created = self.ensure_personnel_exists(TEST_AUTH_CERT_NUMBER, "测试授权人", TEST_DEPT_CODE)
            
            if applicant_created and authorizer_created:
                print("✅ 所有依赖数据准备完成")
                return True
            else:
                print("❌ 依赖数据准备失败")
                return False
                
        except Exception as e:
            print(f"❌ 检查依赖数据时出错: {str(e)}")
            return False
    
    def test_get_equipment_cabinet_records(self):
        """测试获取设备柜记录列表"""
        print("\n=== 测试获取设备柜记录列表 ===")
        
        try:
            response = requests.get(
                EQUIPMENT_CABINET_RECORD_URL,
                headers=self.headers
            )
            
            print(f"获取记录列表响应状态码: {response.status_code}")
            print(f"获取记录列表响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"记录总数: {data.get('total', 0)}")
                print(f"当前页码: {data.get('page', 1)}")
                print(f"每页数量: {data.get('page_size', 10)}")
                print(f"返回记录数: {len(data.get('items', []))}")
                print("✅ 获取设备柜记录列表成功")
                return True
            else:
                print(f"❌ 获取设备柜记录列表失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取设备柜记录列表请求异常: {str(e)}")
            return False
    
    def test_create_equipment_cabinet_record(self):
        """测试创建设备柜记录"""
        print("\n=== 测试创建设备柜记录 ===")
        
        # 先查询实际的申请人信息
        print(f"\n=== 查询实际申请人信息: {TEST_APP_CERT_NUMBER} ===")
        app_response = requests.get(
            f"{PERSONNEL_URL}?certificate_number={TEST_APP_CERT_NUMBER}",
            headers=self.headers
        )
        
        actual_app_cert = TEST_APP_CERT_NUMBER  # 默认使用原证书号
        actual_auth_cert = TEST_AUTH_CERT_NUMBER  # 默认使用原授权证书号
        
        if app_response.status_code == 200:
            app_data = app_response.json()
            if app_data.get("items") and len(app_data.get("items")) > 0:
                print(f"实际申请人信息: {json.dumps(app_data.get('items')[0], ensure_ascii=False)}")
                # 使用返回的certificate_number
                actual_app_cert = app_data.get('items')[0].get('certificate_number')
                print(f"使用实际申请人certificate_number: {actual_app_cert}")
        
        # 再查询实际的授权人信息
        print(f"\n=== 查询实际授权人信息: {TEST_AUTH_CERT_NUMBER} ===")
        auth_response = requests.get(
            f"{PERSONNEL_URL}?certificate_number={TEST_AUTH_CERT_NUMBER}",
            headers=self.headers
        )
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            if auth_data.get("items") and len(auth_data.get("items")) > 0:
                print(f"实际授权人信息: {json.dumps(auth_data.get('items')[0], ensure_ascii=False)}")
                # 使用返回的certificate_number
                actual_auth_cert = auth_data.get('items')[0].get('certificate_number')
                print(f"使用实际授权人certificate_number: {actual_auth_cert}")
        
        # 准备创建记录的数据 - 使用正确的ISO 8601格式，不要末尾的Z
        current_time = datetime.datetime.now(datetime.UTC).isoformat()
        record_data = {
            "dept_code": TEST_DEPT_CODE,
            "device_id": TEST_DEVICE_ID,
            "open_reason_type": "01",
            "applicant_certificate_number": actual_app_cert,
            "application_time": current_time,
            "authorizer_certificate_number": actual_auth_cert,
            "open_type": "01",  # 值班室开启
            "open_result": "01",  # 正常
            "cabinet_open_time": current_time,
            "device_quantity_change": "1->2"
        }
        print(f"创建设备柜记录数据: {json.dumps(record_data, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                EQUIPMENT_CABINET_RECORD_URL,
                json=record_data,
                headers=self.headers
            )
            
            print(f"创建设备柜记录响应状态码: {response.status_code}")
            print(f"创建设备柜记录响应内容: {response.text}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_record_id = data.get("id")
                print(f"✅ 创建设备柜记录成功，记录ID: {self.test_record_id}")
                return True
            else:
                print(f"❌ 创建设备柜记录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 创建设备柜记录请求异常: {str(e)}")
            return False
    
    def test_get_equipment_cabinet_record(self):
        """测试获取单个设备柜记录"""
        print("\n=== 测试获取单个设备柜记录 ===")
        
        if not self.test_record_id:
            # 如果没有记录ID，先查找测试记录
            print("查找测试设备柜记录...")
            response = requests.get(
                f"{EQUIPMENT_CABINET_RECORD_URL}?device_id={TEST_DEVICE_ID}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    self.test_record_id = items[0].get("id")
                    print(f"找到测试设备柜记录，ID: {self.test_record_id}")
                else:
                    print("❌ 未找到测试设备柜记录")
                    return False
            else:
                print(f"❌ 获取设备柜记录列表失败")
                return False
        
        try:
            response = requests.get(
                f"{EQUIPMENT_CABINET_RECORD_URL}/{self.test_record_id}",
                headers=self.headers
            )
            
            print(f"获取单个设备柜记录响应状态码: {response.status_code}")
            print(f"获取单个设备柜记录响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"记录ID: {data.get('id')}")
                print(f"部门编码: {data.get('dept_code')}")
                print(f"设备ID: {data.get('device_id')}")
                print("✅ 获取单个设备柜记录成功")
                return True
            else:
                print(f"❌ 获取单个设备柜记录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取单个设备柜记录请求异常: {str(e)}")
            return False
    
    def test_update_equipment_cabinet_record(self):
        """测试更新设备柜记录"""
        print("\n=== 测试更新设备柜记录 ===")
        
        if not self.test_record_id:
            # 如果没有记录ID，先查找或创建记录
            print("需要先有测试记录才能更新")
            if not self.test_record_id:
                # 先尝试创建记录
                if not self.test_create_equipment_cabinet_record():
                    print("❌ 无法创建测试记录，无法进行更新测试")
                    return False
        
        # 准备更新数据（主要用于关闭设备柜）
        current_time = datetime.datetime.utcnow().isoformat() + 'Z'
        update_data = {
            "cabinet_close_time": current_time,
            "device_quantity_change": "2->1"
        }
        
        try:
            response = requests.put(
                f"{EQUIPMENT_CABINET_RECORD_URL}/{self.test_record_id}",
                json=update_data,
                headers=self.headers
            )
            
            print(f"更新设备柜记录响应状态码: {response.status_code}")
            print(f"更新设备柜记录响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 更新设备柜记录成功")
                return True
            else:
                print(f"❌ 更新设备柜记录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 更新设备柜记录请求异常: {str(e)}")
            return False
    
    def test_delete_equipment_cabinet_record(self):
        """测试删除设备柜记录"""
        print("\n=== 测试删除设备柜记录 ===")
        
        if not self.test_record_id:
            print("需要先有测试记录才能删除")
            return False
        
        try:
            response = requests.delete(
                f"{EQUIPMENT_CABINET_RECORD_URL}/{self.test_record_id}",
                headers=self.headers
            )
            
            print(f"删除设备柜记录响应状态码: {response.status_code}")
            print(f"删除设备柜记录响应内容: {response.text}")
            
            if response.status_code == 204 or response.status_code == 200:
                print("✅ 删除设备柜记录成功")
                # 清除测试记录ID
                self.test_record_id = None
                return True
            else:
                print(f"❌ 删除设备柜记录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 删除设备柜记录请求异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n========== 开始测试设备柜记录API ==========")
        
        # 1. 登录认证
        if not self.login():
            print("\n❌ 登录失败，无法继续测试")
            return False
        
        # 2. 检查依赖数据
        if not self.check_dependencies():
            print("\n❌ 依赖数据准备失败，无法继续测试")
            return False
        
        # 3. 运行CRUD测试
        test_results = []
        
        # 获取记录列表测试
        test_results.append(self.test_get_equipment_cabinet_records())
        
        # 创建记录测试
        test_results.append(self.test_create_equipment_cabinet_record())
        
        # 获取单个记录测试
        test_results.append(self.test_get_equipment_cabinet_record())
        
        # 更新记录测试
        test_results.append(self.test_update_equipment_cabinet_record())
        
        # 删除记录测试
        test_results.append(self.test_delete_equipment_cabinet_record())
        
        # 4. 统计测试结果
        passed_count = sum(1 for result in test_results if result)
        total_count = len(test_results)
        
        print(f"\n========== 测试结果统计 ==========")
        print(f"总测试数: {total_count}")
        print(f"通过测试数: {passed_count}")
        print(f"失败测试数: {total_count - passed_count}")
        print(f"测试通过率: {passed_count / total_count * 100:.1f}%")
        
        return all(test_results)


if __name__ == "__main__":
    tester = EquipmentCabinetRecordApiTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！设备柜记录API测试成功完成。")
    else:
        print("\n❌ 部分测试失败，请检查问题。")
