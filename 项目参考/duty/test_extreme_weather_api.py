#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极端天气值班统计API测试脚本
"""

import requests
import json
import datetime

def get_access_token(base_url):
    """
    获取访问令牌
    
    Args:
        base_url: 基础URL
        
    Returns:
        str: 访问令牌
    """
    print(f"\n正在登录获取访问令牌...")
    login_url = f"{base_url}/api/v1/auth/login/form"
    
    # 使用默认的管理员账号登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 使用表单数据而不是JSON
        response = requests.post(login_url, data=login_data)
        response.raise_for_status()
        data = response.json()
        
        if "access_token" in data:
            print(f"✅ 登录成功，获取到访问令牌")
            return data["access_token"]
        else:
            print(f"❌ 登录失败，响应中没有access_token字段")
            print(f"登录响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录请求异常: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 登录过程中发生错误: {str(e)}")
        return None

def test_extreme_weather_duty_api():
    """
    测试极端天气值班统计API
    """
    print("=" * 60)
    print("极端天气值班统计API测试")
    print("=" * 60)
    
    # API端点URL
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/analytics/extreme-weather-duty"
    url = f"{base_url}{endpoint}"
    
    # 获取访问令牌
    access_token = get_access_token(base_url)
    if not access_token:
        print("\n❌ 无法获取访问令牌，测试失败！")
        return False
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 测试参数
    params = {
        "personnel_id": "ZHANG001",  # 使用别名参数
        "year": "2025"
    }
    
    print(f"\n测试极端天气值班统计API...")
    print(f"目标URL: {url}")
    
    try:
        # 发送GET请求，带认证头
        response = requests.get(url, params=params, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"❌ 服务器错误: HTTP {response.status_code}")
            if response.content:
                try:
                    error_data = response.json()
                    print(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                except:
                    print(f"错误详情: {response.text}")
            return False
        
        # 解析响应数据
        data = response.json()
        
        print(f"✅ API调用成功！")
        print(f"\n响应数据结构验证:")
        
        # 验证响应数据结构
        required_fields = ["personnel_id", "personnel_name", "year", "total_duty_days", 
                          "total_duty_hours", "total_duty_records", "extreme_duty_records", 
                          "weather_type_summary"]
        
        # 检查必需字段是否存在
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"❌ 缺失必需字段: {missing_fields}")
            return False
        
        print(f"✅ 所有必需字段都存在")
        
        # 验证字段类型
        type_checks = [
            ("personnel_id", str),
            ("personnel_name", str),
            ("year", str),
            ("total_duty_days", int),
            ("total_duty_hours", (int, float)),
            ("total_duty_records", int),
            ("extreme_duty_records", list),
            ("weather_type_summary", list)
        ]
        
        type_errors = []
        for field, expected_type in type_checks:
            if not isinstance(data[field], expected_type):
                type_errors.append(f"{field}: 期望类型 {expected_type.__name__ if isinstance(expected_type, type) else expected_type}, 实际类型 {type(data[field]).__name__}")
        
        if type_errors:
            print(f"❌ 字段类型错误:")
            for error in type_errors:
                print(f"  - {error}")
        else:
            print(f"✅ 所有字段类型正确")
        
        # 验证extreme_duty_records列表中每个元素的结构
        if data["extreme_duty_records"]:
            print(f"\n极端值班记录验证:")
            record_fields = ["duty_id", "duty_date"]
            valid_records = True
            
            for i, record in enumerate(data["extreme_duty_records"][:5]):  # 只检查前5条记录
                missing_record_fields = [field for field in record_fields if field not in record]
                if missing_record_fields:
                    print(f"❌ 记录 {i} 缺失字段: {missing_record_fields}")
                    valid_records = False
                
                # 验证duty_date是否为有效的日期格式
                try:
                    datetime.datetime.fromisoformat(record["duty_date"])
                except ValueError:
                    print(f"❌ 记录 {i} 的duty_date格式错误: {record['duty_date']}")
                    valid_records = False
            
            if valid_records:
                print(f"✅ 极端值班记录结构正确")
        
        # 验证weather_type_summary列表中每个元素的结构
        if data["weather_type_summary"]:
            print(f"\n天气类型汇总验证:")
            summary_fields = ["type", "count"]
            valid_summaries = True
            
            for i, summary in enumerate(data["weather_type_summary"][:5]):  # 只检查前5条记录
                missing_summary_fields = [field for field in summary_fields if field not in summary]
                if missing_summary_fields:
                    print(f"❌ 天气类型 {i} 缺失字段: {missing_summary_fields}")
                    valid_summaries = False
                
                # 验证count是否为整数
                if not isinstance(summary["count"], int):
                    print(f"❌ 天气类型 {i} 的count不是整数: {summary['count']}")
                    valid_summaries = False
            
            if valid_summaries:
                print(f"✅ 天气类型汇总结构正确")
        
        # 打印部分响应数据作为示例
        print(f"\n响应数据示例:")
        print(f"人员ID: {data['personnel_id']}")
        print(f"人员姓名: {data['personnel_name']}")
        print(f"年份: {data['year']}")
        print(f"总值班天数: {data['total_duty_days']}")
        print(f"总值班小时数: {data['total_duty_hours']}")
        print(f"总值班记录数: {data['total_duty_records']}")
        print(f"极端值班记录数: {len(data['extreme_duty_records'])}")
        print(f"天气类型汇总数: {len(data['weather_type_summary'])}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
        print(f"响应内容: {response.text}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生未知错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_extreme_weather_duty_api()
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试成功！")
        exit(0)
    else:
        print("❌ 测试失败！")
        exit(1)
