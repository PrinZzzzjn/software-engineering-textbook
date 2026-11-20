import requests
import json
import time

class WorkstationApiTester:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.login_url = f"{base_url}/auth/login"
        self.workstation_base_url = f"{base_url}/workstation"
        self.token = None
        self.headers = None
        self.test_workstation_id = f"TESTWS{int(time.time())}"  # 生成唯一的测试工位ID
        self.results = {
            "login": {"success": False, "message": ""},
            "create": {"success": False, "message": ""},
            "get_single": {"success": False, "message": ""},
            "update": {"success": False, "message": ""},
            "get_list": {"success": False, "message": ""},
            "delete": {"success": False, "message": ""}
        }

    def login(self, username="admin", password="admin123"):
        """登录获取访问令牌"""
        try:
            print(f"\n[测试] 登录系统...")
            print(f"登录URL: {self.login_url}")
            print(f"用户名: {username}")
            
            response = requests.post(
                self.login_url,
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    }
                    self.results["login"]["success"] = True
                    self.results["login"]["message"] = "登录成功"
                    print(f"✓ 登录成功! 已获取访问令牌")
                    return True
                else:
                    self.results["login"]["message"] = f"登录失败: 未返回访问令牌 - {response.text}"
                    print(f"✗ 登录失败: 未返回访问令牌")
                    return False
            else:
                self.results["login"]["message"] = f"登录失败: 状态码 {response.status_code} - {response.text}"
                print(f"✗ 登录失败: 状态码 {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            self.results["login"]["message"] = f"登录异常: {str(e)}"
            print(f"✗ 登录异常: {str(e)}")
            return False

    def test_create_workstation(self):
        """测试创建工位"""
        try:
            print(f"\n[测试] 创建工位...")
            if not self.token:
                print("✗ 创建失败: 未登录或令牌无效")
                return False

            # 测试数据 - 确保使用有效的dept_code（这里假设DEPT001是有效的）
            workstation_data = {
                "workstation_id": self.test_workstation_id,
                "workstation_name": "测试工位",
                "dept_code": "DEPT001",
                "category_code": "CAT001",
                "longitude": 116.3974,
                "latitude": 39.9093,
                "remark": "测试用工位数据"
            }
            
            url = f"{self.workstation_base_url}/"
            print(f"创建URL: {url}")
            print(f"工位数据: {workstation_data}")
            
            response = requests.post(
                url,
                headers=self.headers,
                json=workstation_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.results["create"]["success"] = True
                self.results["create"]["message"] = "工位创建成功"
                print(f"✓ 工位创建成功!")
                print(f"返回数据: {json.dumps(data, ensure_ascii=False)}")
                return True
            else:
                self.results["create"]["message"] = f"工位创建失败: 状态码 {response.status_code} - {response.text}"
                print(f"✗ 工位创建失败: 状态码 {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            self.results["create"]["message"] = f"创建工位异常: {str(e)}"
            print(f"✗ 创建工位异常: {str(e)}")
            return False

    def test_get_workstation(self):
        """测试获取单个工位信息"""
        try:
            print(f"\n[测试] 获取单个工位信息...")
            if not self.token:
                print("✗ 获取失败: 未登录或令牌无效")
                return False

            url = f"{self.workstation_base_url}/{self.test_workstation_id}"
            print(f"获取URL: {url}")
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.results["get_single"]["success"] = True
                self.results["get_single"]["message"] = "获取工位信息成功"
                print(f"✓ 获取工位信息成功!")
                print(f"返回数据: {json.dumps(data, ensure_ascii=False)}")
                return True
            else:
                self.results["get_single"]["message"] = f"获取工位信息失败: 状态码 {response.status_code} - {response.text}"
                print(f"✗ 获取工位信息失败: 状态码 {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            self.results["get_single"]["message"] = f"获取工位信息异常: {str(e)}"
            print(f"✗ 获取工位信息异常: {str(e)}")
            return False

    def test_update_workstation(self):
        """测试更新工位信息"""
        try:
            print(f"\n[测试] 更新工位信息...")
            if not self.token:
                print("✗ 更新失败: 未登录或令牌无效")
                return False

            # 更新数据
            update_data = {
                "workstation_name": "测试工位-已更新",
                "remark": "已更新的测试工位备注"
            }
            
            url = f"{self.workstation_base_url}/{self.test_workstation_id}"
            print(f"更新URL: {url}")
            print(f"更新数据: {update_data}")
            
            response = requests.put(
                url,
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.results["update"]["success"] = True
                self.results["update"]["message"] = "工位更新成功"
                print(f"✓ 工位更新成功!")
                print(f"返回数据: {json.dumps(data, ensure_ascii=False)}")
                return True
            else:
                self.results["update"]["message"] = f"工位更新失败: 状态码 {response.status_code} - {response.text}"
                print(f"✗ 工位更新失败: 状态码 {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            self.results["update"]["message"] = f"更新工位异常: {str(e)}"
            print(f"✗ 更新工位异常: {str(e)}")
            return False

    def test_get_workstation_list(self):
        """测试获取工位列表"""
        try:
            print(f"\n[测试] 获取工位列表...")
            if not self.token:
                print("✗ 获取列表失败: 未登录或令牌无效")
                return False

            # 查询参数
            params = {
                "page": 1,
                "page_size": 10,
                "workstation_name": "测试工位"
            }
            
            url = f"{self.workstation_base_url}/"
            print(f"列表URL: {url}")
            print(f"查询参数: {params}")
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                self.results["get_list"]["success"] = True
                self.results["get_list"]["message"] = "获取工位列表成功"
                print(f"✓ 获取工位列表成功!")
                print(f"总记录数: {data.get('total', 0)}")
                print(f"当前页: {data.get('page', 0)}/{data.get('pages', 0)}")
                print(f"本页数据数: {len(data.get('items', []))}")
                return True
            else:
                self.results["get_list"]["message"] = f"获取工位列表失败: 状态码 {response.status_code} - {response.text}"
                print(f"✗ 获取工位列表失败: 状态码 {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            self.results["get_list"]["message"] = f"获取工位列表异常: {str(e)}"
            print(f"✗ 获取工位列表异常: {str(e)}")
            return False

    def test_delete_workstation(self):
        """测试删除工位"""
        try:
            print(f"\n[测试] 删除工位...")
            if not self.token:
                print("✗ 删除失败: 未登录或令牌无效")
                return False

            url = f"{self.workstation_base_url}/{self.test_workstation_id}"
            print(f"删除URL: {url}")
            
            response = requests.delete(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.results["delete"]["success"] = True
                self.results["delete"]["message"] = "工位删除成功"
                print(f"✓ 工位删除成功!")
                print(f"返回数据: {json.dumps(data, ensure_ascii=False)}")
                return True
            else:
                self.results["delete"]["message"] = f"工位删除失败: 状态码 {response.status_code} - {response.text}"
                print(f"✗ 工位删除失败: 状态码 {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            self.results["delete"]["message"] = f"删除工位异常: {str(e)}"
            print(f"✗ 删除工位异常: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试并输出结果摘要"""
        print("="*60)
        print("工位模块API功能测试")
        print("="*60)
        
        # 按顺序运行测试
        tests = [
            ("login", self.login),
            ("create", self.test_create_workstation),
            ("get_single", self.test_get_workstation),
            ("update", self.test_update_workstation),
            ("get_list", self.test_get_workstation_list),
            ("delete", self.test_delete_workstation)
        ]
        
        for test_name, test_func in tests:
            # 跳过后续测试如果登录失败
            if test_name != "login" and not self.results["login"]["success"]:
                print(f"\n[测试] {test_name} 跳过: 登录失败")
                continue
            
            test_func()
            # 短暂延迟避免请求过快
            if test_name != "delete":  # 最后一个测试不需要延迟
                time.sleep(0.5)
        
        # 输出测试结果摘要
        self.print_test_summary()
        return all(result["success"] for result in self.results.values())

    def print_test_summary(self):
        """打印测试结果摘要"""
        print("\n" + "="*60)
        print("测试结果摘要")
        print("="*60)
        
        success_count = sum(1 for result in self.results.values() if result["success"])
        total_count = len(self.results)
        
        for test_name, result in self.results.items():
            status = "✓ 成功" if result["success"] else "✗ 失败"
            print(f"{test_name.upper()}: {status}")
            if not result["success"]:
                print(f"  原因: {result['message']}")
        
        print("="*60)
        print(f"总体结果: {success_count}/{total_count} 测试通过")
        print("="*60)

if __name__ == "__main__":
    tester = WorkstationApiTester()
    tester.run_all_tests()
