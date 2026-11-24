#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试值班数据脚本
用于创建部门、工位、人员和2025年的值班记录
"""

import random
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.base_model import Base

# 导入模型
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.workstation.model import Workstation
from app.api.v1.module_duty.personnel.model import Personnel
from app.api.v1.module_duty.duty_record.model import DutyRecord


def create_database_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def get_or_create_department(db: Session, dept_code: str, full_name: str) -> Department:
    """获取或创建部门"""
    dept = db.query(Department).filter(Department.dept_code == dept_code).first()
    if not dept:
        dept = Department(
            dept_code=dept_code,
            full_name=full_name,
            address="测试地址",
            longitude=116.3974,
            latitude=39.9093
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)
        print(f"创建部门: {full_name} ({dept_code})")
    else:
        print(f"部门已存在: {full_name} ({dept_code})")
    return dept


def get_or_create_workstation(db: Session, workstation_id: str, workstation_name: str, dept_code: str) -> Workstation:
    """获取或创建工位"""
    workstation = db.query(Workstation).filter(Workstation.workstation_id == workstation_id).first()
    if not workstation:
        workstation = Workstation(
            workstation_id=workstation_id,
            workstation_name=workstation_name,
            dept_code=dept_code,
            category_code="CATEGORY001",
            longitude=116.3974,
            latitude=39.9093,
            remark="测试工位"
        )
        db.add(workstation)
        db.commit()
        db.refresh(workstation)
        print(f"创建工位: {workstation_name} ({workstation_id})")
    else:
        print(f"工位已存在: {workstation_name} ({workstation_id})")
    return workstation


def get_or_create_personnel(db: Session, name: str, certificate_number: str, id_card_number: str, dept_code: str) -> Personnel:
    """获取或创建人员"""
    person = db.query(Personnel).filter(Personnel.certificate_number == certificate_number).first()
    if not person:
        person = Personnel(
            name=name,
            certificate_number=certificate_number,
            id_card_number=id_card_number,
            dept_code=dept_code,
            position="值班员",
            rank="普通",
            hire_date=date(2020, 1, 1)
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        print(f"创建人员: {name} ({certificate_number})")
    else:
        print(f"人员已存在: {name} ({certificate_number})")
    return person


def generate_duty_records(db: Session, personnel: list, workstations: list, year: int = 2025, count: int = 20):
    """生成值班记录"""
    # 计算2025年的开始和结束日期
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # 生成指定数量的值班记录
    generated_count = 0
    max_attempts = count * 3  # 最大尝试次数，避免死循环
    attempts = 0
    
    while generated_count < count and attempts < max_attempts:
        attempts += 1
        
        # 随机选择人员
        person = random.choice(personnel)
        
        # 随机选择工位
        workstation = random.choice(workstations)
        
        # 随机生成日期（2025年范围内）
        days_delta = random.randint(0, (end_date - start_date).days)
        record_date = start_date + timedelta(days=days_delta)
        
        # 随机生成开始时间（整点左右几分钟）
        hour = random.randint(0, 23)
        minute = random.randint(-5, 5)  # 整点前后5分钟
        if minute < 0:
            minute = 60 + minute
            hour = (hour - 1) % 24
        
        start_time = datetime.combine(record_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
        
        # 随机生成持续时间（2小时左右，上下几分钟）
        duration_minutes = 120 + random.randint(-5, 5)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # 检查是否与现有记录冲突（简化检查，避免同一人同一天同一时间段有重叠）
        conflicting = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == person.certificate_number,
            DutyRecord.start_time <= end_time,
            DutyRecord.end_time >= start_time
        ).first()
        
        if not conflicting:
            # 随机选择不同的人员作为接班人
            other_personnel = [p for p in personnel if p.certificate_number != person.certificate_number]
            successor = random.choice(other_personnel) if other_personnel else None
            
            # 创建值班记录
            duty_record = DutyRecord(
                personnel_certificate_number=person.certificate_number,
                successor_certificate_number=successor.certificate_number if successor else None,
                start_time=start_time,
                end_time=end_time,
                workstation_id=workstation.workstation_id,
                status="normal",
                remark=f"自动生成的测试值班记录",
                created_by="system"
            )
            db.add(duty_record)
            generated_count += 1
            successor_name = successor.name if successor else "无"
            print(f"生成值班记录 {generated_count}/{count}: {person.name} {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}, 接班人: {successor_name}")
    
    # 批量提交
    if generated_count > 0:
        db.commit()
    
    return generated_count


def main():
    """主函数"""
    print("开始生成测试数据...")
    
    # 创建数据库表
    create_database_tables()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 1. 创建部门
        dept = get_or_create_department(db, "DEPT001", "测试部门")
        
        # 2. 创建工位
        workstation1 = get_or_create_workstation(db, "WS001", "测试工位1", dept.dept_code)
        workstation2 = get_or_create_workstation(db, "WS002", "测试工位2", dept.dept_code)
        workstations = [workstation1, workstation2]
        
        # 3. 创建人员
        zhang_san = get_or_create_personnel(db, "张伟", "ZHANG001", "110101199001010001", dept.dept_code)
        li_si = get_or_create_personnel(db, "李四", "LI001", "110101199002020002", dept.dept_code)
        personnel = [zhang_san, li_si]
        
        # 4. 生成值班记录
        print("\n开始生成值班记录...")
        generated_count = generate_duty_records(db, personnel, workstations, year=2025, count=20)
        print(f"\n成功生成 {generated_count} 条值班记录")
        
    except Exception as e:
        print(f"生成数据时出错: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n测试数据生成完成")


if __name__ == "__main__":
    main()
