#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加默认管理员账号脚本
用于创建或更新管理员用户账号
"""
import os
import sys
from pathlib import Path
import argparse

# 添加项目根目录到sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

def create_or_update_admin(username='admin', password='admin123', role='ADMIN', is_active=True):
    """
    创建或更新管理员用户
    
    Args:
        username: 管理员用户名
        password: 管理员密码
        role: 用户角色（ADMIN 或 USER）
        is_active: 是否激活
        
    Returns:
        bool: 操作是否成功
    """
    try:
        print(f"开始创建/更新管理员用户: {username}")
        
        # 导入必要的模块
        from app.core.database import SessionLocal
        from app.api.v1.module_system.user.model import User, UserRole
        from app.core.security import get_password_hash
        
        # 验证角色值
        if role not in ['ADMIN', 'USER']:
            print(f"错误: 无效的角色值 '{role}'，必须是 'ADMIN' 或 'USER'")
            return False
            
        # 将字符串角色转换为枚举值
        role_enum = UserRole.ADMIN if role == 'ADMIN' else UserRole.USER
        
        db = SessionLocal()
        try:
            # 检查是否已存在用户
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                # 创建新用户
                user = User(
                    username=username,
                    password_hash=get_password_hash(password),
                    role=role_enum,
                    is_active=1 if is_active else 0
                )
                db.add(user)
                db.commit()
                print(f"管理员用户创建成功: {username}")
                print(f"用户名: {username}")
                print(f"密码: {password}")
                print(f"角色: {role}")
                print(f"状态: {'激活' if is_active else '未激活'}")
            else:
                # 更新现有用户
                user.password_hash = get_password_hash(password)
                user.role = role_enum
                user.is_active = 1 if is_active else 0
                db.commit()
                print(f"管理员用户更新成功: {username}")
                print(f"用户名: {username}")
                print(f"密码: {password}")
                print(f"角色: {role}")
                print(f"状态: {'激活' if is_active else '未激活'}")
                
            return True
            
        except Exception as e:
            db.rollback()
            print(f"数据库操作失败: {str(e)}")
            return False
        finally:
            db.close()
            
    except ImportError as e:
        print(f"导入模块失败: {str(e)}")
        print("请确保应用环境已正确设置，并且所有依赖已安装")
        return False
    except Exception as e:
        print(f"创建/更新管理员用户失败: {str(e)}")
        return False

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='创建或更新管理员用户')
    
    parser.add_argument('--username', type=str, default='admin', help='管理员用户名 (默认: admin)')
    parser.add_argument('--password', type=str, default='admin123', help='管理员密码 (默认: admin123)')
    parser.add_argument('--role', type=str, default='ADMIN', choices=['ADMIN', 'USER'], help='用户角色 (默认: ADMIN)')
    parser.add_argument('--inactive', action='store_true', help='创建非激活状态的用户')
    
    args = parser.parse_args()
    
    # 执行创建或更新操作
    success = create_or_update_admin(
        username=args.username,
        password=args.password,
        role=args.role,
        is_active=not args.inactive
    )
    
    if success:
        print("=== 操作完成 ===")
        sys.exit(0)
    else:
        print("=== 操作失败 ===")
        sys.exit(1)


if __name__ == "__main__":
    main()