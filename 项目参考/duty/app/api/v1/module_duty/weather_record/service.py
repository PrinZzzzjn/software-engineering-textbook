from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.v1.module_duty.weather_record.crud import weather_record_crud
from app.api.v1.module_duty.weather_record.schemas import (
    WeatherRecordCreate,
    WeatherRecordUpdate,
    WeatherRecordResponse
)
from app.api.v1.module_duty.weather_record.param import WeatherRecordQueryParams, WeatherRecordDeleteByDeptParams
from app.core.exceptions import NotFoundException

class WeatherRecordService:
    """天气记录业务逻辑层"""
    
    def create_record(self, db: Session, record_data: WeatherRecordCreate) -> WeatherRecordResponse:
        """创建天气记录"""
        # 检查是否已存在相同时间和部门的记录
        existing = weather_record_crud.get_by_location_and_time(
            db,
            dept_code=record_data.dept_code,
            record_time=record_data.record_time
        )
        
        if existing:
            raise ValueError("该时间点该部门已存在天气记录")
        
        # 直接创建记录
        create_data = record_data.model_dump()
        db_record = weather_record_crud.create(db, create_data)
        
        # 转换为响应格式
        return self._convert_to_response(db_record)
    
    def get_records_list(self, db: Session, params: WeatherRecordQueryParams) -> Dict[str, Any]:
        """获取天气记录列表（分页）"""
        # 参数校验
        if params.start_time and params.end_time and params.start_time > params.end_time:
            raise ValueError("开始时间不能晚于结束时间")
        
        # 获取分页数据
        result = weather_record_crud.get_paginated_list(db, params)
        
        # 转换为响应格式
        items = [self._convert_to_response(item) for item in result['items']]
        
        return {
            "items": items,
            "total": result['total'],
            "page": result['page'],
            "page_size": result['page_size'],
            "pages": result['pages']
        }
    
    def get_record_by_id(self, db: Session, id: int) -> WeatherRecordResponse:
        """根据ID获取天气记录"""
        record = weather_record_crud.get_by_id(db, id)
        if not record:
            raise NotFoundException(f"天气记录不存在: {id}")
        
        return self._convert_to_response(record)
    
    def update_record(self, db: Session, id: int, update_data: WeatherRecordUpdate) -> WeatherRecordResponse:
        """更新天气记录"""
        # 获取现有记录
        db_record = weather_record_crud.get_by_id(db, id)
        if not db_record:
            raise NotFoundException(f"天气记录不存在: {id}")
        
        # 转换更新数据
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 更新记录
        updated_record = weather_record_crud.update(db, db_record, update_dict)
        
        return self._convert_to_response(updated_record)
    
    def delete_record(self, db: Session, id: int) -> bool:
        """删除天气记录"""
        # 检查记录是否存在
        if not weather_record_crud.get_by_id(db, id):
            raise NotFoundException(f"天气记录不存在: {id}")
        
        return weather_record_crud.delete(db, id)
        
    def delete_records_by_dept_code(self, db: Session, params: WeatherRecordDeleteByDeptParams) -> Dict[str, Any]:
        """
        按部门代码删除天气记录
        
        Args:
            db: 数据库会话
            params: 删除参数，包含部门代码和可选的时间范围
            
        Returns:
            Dict[str, Any]: 删除结果，包含删除的记录数量和消息
        """
        # 调用CRUD层方法执行删除
        deleted_count = weather_record_crud.delete_by_dept_code(
            db=db,
            dept_code=params.dept_code,
            start_time=params.start_time,
            end_time=params.end_time
        )
        
        # 构建返回结果
        return {
            "deleted_count": deleted_count,
            "message": f"成功删除部门 {params.dept_code} 的天气记录 {deleted_count} 条"
        }
    
    def batch_import_records(self, db: Session, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量导入天气记录
        
        Args:
            db: 数据库会话
            records: 天气记录列表
            
        Returns:
            Dict[str, Any]: 包含成功和失败信息的字典
        """
        try:
            # 过滤掉已经在controller层标记为错误的记录
            valid_records = [record for record in records if 'error' not in record]
            
            # 调用crud层的batch_create方法
            result = weather_record_crud.batch_create(db, valid_records)
            
            # 合并controller层已经识别的错误
            controller_errors = [record for record in records if 'error' in record]
            if controller_errors:
                result['failed_count'] += len(controller_errors)
                result['failed_records'].extend(controller_errors)
            
            return result
        except Exception as e:
            # 处理导入过程中的异常
            raise Exception(f"批量导入天气记录失败: {str(e)}")
    
    def _convert_to_response(self, db_record: Any) -> WeatherRecordResponse:
        """将数据库记录转换为响应模型"""
        # 转换数据
        data = {
            "id": db_record.id,
            "record_time": db_record.record_time,
            "dept_code": db_record.dept_code,
            "temperature": db_record.temperature,
            "humidity": db_record.humidity,
            "rainfall": db_record.rainfall,
            "snowfall": db_record.snowfall,
            "wind_speed": db_record.wind_speed,
            "weather_conditions": db_record.weather_conditions_array  # 使用新的属性获取数组格式
        }
        
        return WeatherRecordResponse(**data)

# 创建service实例
weather_record_service = WeatherRecordService()
