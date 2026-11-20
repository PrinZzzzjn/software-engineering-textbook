from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.base_crud import BaseCRUD
from app.api.v1.module_duty.weather_record.model import WeatherRecord
from app.api.v1.module_duty.weather_record.param import WeatherRecordQueryParams

class WeatherRecordCrud(BaseCRUD):
    """天气记录数据访问层"""
    
    def __init__(self):
        super().__init__(WeatherRecord)
    
    def get_by_id(self, db: Session, id: int) -> Optional[WeatherRecord]:
        """根据ID获取天气记录"""
        return db.query(WeatherRecord).filter(WeatherRecord.id == id).first()
    
    def get_by_location_and_time(self, db: Session, dept_code: str, record_time: datetime) -> Optional[WeatherRecord]:
        """根据部门代码和时间获取天气记录"""
        return db.query(WeatherRecord).filter(
            and_(
                WeatherRecord.dept_code == dept_code,
                WeatherRecord.record_time == record_time
            )
        ).first()
    
    def get_paginated_list(self, db: Session, params: WeatherRecordQueryParams) -> Dict[str, Any]:
        """获取分页的天气记录列表"""
        # 构建查询条件
        query = db.query(WeatherRecord)
        
        # 时间范围筛选
        if params.start_time:
            query = query.filter(WeatherRecord.record_time >= params.start_time)
        if params.end_time:
            query = query.filter(WeatherRecord.record_time <= params.end_time)
        
        # 部门代码筛选
        if hasattr(params, 'dept_code') and params.dept_code is not None:
            query = query.filter(WeatherRecord.dept_code == params.dept_code)
        
        # 按时间倒序排序
        query = query.order_by(WeatherRecord.record_time.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        items = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
        
        # 计算总页数
        pages = (total + params.page_size - 1) // params.page_size
        
        return {
            "items": items,
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "pages": pages
        }
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> WeatherRecord:
        """创建天气记录"""
        db_obj = WeatherRecord(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: WeatherRecord, obj_in: Dict[str, Any]) -> WeatherRecord:
        """更新天气记录"""
        # 只更新提供的字段
        update_data = {k: v for k, v in obj_in.items() if v is not None}
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """删除天气记录"""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True
        
    def delete_by_dept_code(self, db: Session, dept_code: str, start_time=None, end_time=None) -> int:
        """
        按部门代码删除天气记录
        
        Args:
            db: 数据库会话
            dept_code: 部门代码
            start_time: 可选的开始时间
            end_time: 可选的结束时间
            
        Returns:
            int: 删除的记录数量
        """
        # 构建查询条件
        conditions = [WeatherRecord.dept_code == dept_code]
        
        # 添加时间范围筛选条件
        if start_time:
            conditions.append(WeatherRecord.record_time >= start_time)
        if end_time:
            conditions.append(WeatherRecord.record_time <= end_time)
        
        # 执行删除操作
        deleted_count = db.query(WeatherRecord).filter(*conditions).delete()
        db.commit()
        
        return deleted_count
    
    def batch_create(self, db: Session, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量创建天气记录，返回成功和失败的统计信息
        采用批量检查重复记录的方式，减少数据库查询次数
        
        Args:
            db: 数据库会话
            records: 天气记录列表
            
        Returns:
            Dict[str, Any]: 包含success_count, failed_count, failed_records的字典
        """
        success_count = 0
        failed_count = 0
        failed_records = []
        
        # 收集需要检查重复的记录信息
        valid_records_with_row = []
        for record_data in records:
            # 确保记录有必要的字段
            if '_row' in record_data and 'dept_code' in record_data and 'record_time' in record_data:
                valid_records_with_row.append(record_data)
            else:
                # 无效记录，直接标记为失败
                row_number = record_data.get('_row', 'Unknown')
                failed_count += 1
                failed_records.append({
                    'row': row_number,
                    'error': "记录缺少必要字段"
                })
        
        if not valid_records_with_row:
            return {
                "success_count": 0,
                "failed_count": failed_count,
                "failed_records": failed_records
            }
        
        # 批量查询数据库中已存在的记录
        # 提取所有部门代码和记录时间组合
        dept_codes = [record['dept_code'] for record in valid_records_with_row]
        record_times = [record['record_time'] for record in valid_records_with_row]
        
        # 批量查询已存在的记录
        existing_records = db.query(WeatherRecord).filter(
            WeatherRecord.dept_code.in_(set(dept_codes)),
            WeatherRecord.record_time.in_(set(record_times))
        ).all()
        
        # 创建已存在记录的映射，用于快速检查
        existing_record_map = {
            (record.dept_code, record.record_time): True 
            for record in existing_records
        }
        
        # 处理每条记录
        for record_data in valid_records_with_row:
            # 获取行号信息
            row_number = record_data.pop('_row', 'Unknown')
            # 复制记录数据，避免修改原始数据
            record_copy = record_data.copy()
            
            try:
                # 使用映射快速检查是否存在重复记录
                key = (record_copy['dept_code'], record_copy['record_time'])
                if key in existing_record_map:
                    failed_count += 1
                    failed_records.append({
                        'row': row_number,
                        'error': "该时间点该部门已存在天气记录"
                    })
                else:
                    # 创建新记录
                    weather_record = WeatherRecord(**record_copy)
                    db.add(weather_record)
                    # 添加到已存在映射中，避免后续记录重复检查
                    existing_record_map[key] = True
                    success_count += 1
            except Exception as e:
                failed_count += 1
                failed_records.append({
                    'row': row_number,
                    'error': f"创建记录失败: {str(e)}"
                })
        
        # 提交事务
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"事务提交失败: {str(e)}")
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_records": failed_records
        }

# 创建crud实例
weather_record_crud = WeatherRecordCrud()
