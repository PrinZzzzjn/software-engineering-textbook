#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专门用于清空weather_records表数据的脚本
保留表结构，只删除现有数据
"""
import sys
from pathlib import Path

# 添加项目根目录到sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


def clear_weather_records():
    """清空weather_records表的数据"""
    print("=== 开始清空weather_records表数据 ===")
    
    try:
        # 导入必要的模块
        from app.core.database import SessionLocal, engine
        from sqlalchemy import text
        
        print("连接到数据库...")
        
        # 使用事务清空表
        with engine.begin() as conn:
            # 检查weather_records表是否存在（适用于SQLite）
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='weather_records'
            """))
            table_exists = result.fetchone() is not None
            
            if table_exists:
                print("正在清空weather_records表数据...")
                # 清空表但保留结构
                conn.execute(text("DELETE FROM weather_records"))
                print("weather_records表数据清空成功！")
            else:
                print("weather_records表不存在，跳过清空操作")
                # 如果表不存在，可以选择创建它
                print("创建weather_records表...")
                from app.core.database import Base
                import app.api.v1.module_duty.weather_record.model
                Base.metadata.create_all(bind=engine)
                print("weather_records表创建成功")
        
        print("=== weather_records表数据清空操作完成 ===")
        return True
    except Exception as e:
        print(f"清空weather_records表数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    if clear_weather_records():
        print("操作成功完成！")
        sys.exit(0)
    else:
        print("操作失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
