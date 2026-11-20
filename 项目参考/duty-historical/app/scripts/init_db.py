#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建初始迁移并执行数据库迁移
"""
import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


def run_command(command, cwd=None):
    """执行命令并显示输出"""
    print(f"执行命令: {' '.join(command)}")
    try:
        # 直接使用alembic命令，而不是通过Python模块方式
        result = subprocess.run(
            command,
            cwd=cwd or PROJECT_ROOT,
            shell=True,  # 在Windows上使用shell=True
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"命令成功执行: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e.stderr}")
        return False


def reset_alembic_state():
    """重置alembic状态"""
    print("重置alembic状态...")
    try:
        # 导入必要的模块
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # 尝试删除可能存在的索引
            try:
                conn.execute(text("DROP INDEX IF EXISTS idx_record_time"))
                conn.execute(text("DROP INDEX IF EXISTS idx_workstation_time"))
            except Exception:
                # 如果索引不存在，忽略错误
                pass
            # 显式删除weather_records表，确保表结构被完全重建
            conn.execute(text("DROP TABLE IF EXISTS weather_records"))
            # 删除alembic版本表（如果存在）
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()
        print("alembic状态重置成功，索引和weather_records表已删除")
        return True
    except Exception as e:
        print(f"重置alembic状态失败: {str(e)}")
        return False

def init_migrations():
    """初始化数据库迁移"""
    print("=== 开始初始化数据库迁移 ===")
    
    # 重置alembic状态
    reset_alembic_state()
    
    # 直接使用SQLAlchemy创建所有表
    print("创建数据库表...")
    try:
        from app.core.database import Base
        from app.core.database import engine
        
        # 导入所有模型以确保它们被注册
        import app.api.v1.module_duty.dept.model
        import app.api.v1.module_duty.personnel.model
        import app.api.v1.module_duty.workstation.model
        import app.api.v1.module_duty.duty_record.model
        import app.api.v1.module_duty.inspection_record.model
        import app.api.v1.module_duty.weather_record.model
        import app.api.v1.module_system.user.model
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")
        
        # 初始化alembic版本表
        print("初始化alembic版本...")
        if not run_command([
            'alembic', 'stamp', 'head'
        ]):
            print("初始化alembic版本失败，但表已创建成功")
        
        print("=== 数据库迁移初始化完成 ===")
        return True
    except Exception as e:
        print(f"创建数据库表失败: {str(e)}")
        return False


def create_admin_user():
    """创建管理员用户（可选）"""
    try:
        # 导入必要的模块
        from app.core.database import SessionLocal
        from app.api.v1.module_system.user.model import User, UserRole
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        try:
            # 检查是否已存在管理员用户
            admin_user = db.query(User).filter(User.username == 'admin').first()
            if not admin_user:
                # 创建管理员用户
                admin_user = User(
                    username='admin',
                    password_hash=get_password_hash('admin123'),
                    role=UserRole.ADMIN,
                    is_active=1
                )
                db.add(admin_user)
                db.commit()
                print("管理员用户创建成功: username=admin, password=admin123")
            else:
                print("管理员用户已存在")
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"创建管理员用户失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 初始化数据库迁移
    if init_migrations():
        # 创建管理员用户（可选）
        create_admin_user()
        print("数据库初始化完成！")
    else:
        print("数据库初始化失败！")
        sys.exit(1)
