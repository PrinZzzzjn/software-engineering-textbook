# 节假日CRUD操作 - 使用局部导入避免循环依赖
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_


class HolidayCRUD:
    """节假日CRUD操作类"""
    
    @staticmethod
    def create(db: Session, holiday_data: Any) -> Any:
        """创建节假日"""
        # 局部导入，避免循环依赖
        from .models import Holiday, HolidayType
        
        # 检查日期是否已存在
        existing = db.query(Holiday).filter(Holiday.date == holiday_data.date).first()
        if existing:
            raise ValueError(f"日期 {holiday_data.date} 已存在节假日记录")
        
        # 创建新记录
        holiday_dict = holiday_data.model_dump()
        
        # 特殊处理holiday_type枚举值转换
        if holiday_dict.get('holiday_type'):
            holiday_type_value = holiday_dict['holiday_type']
            
            # 如果是字符串，验证并保持字符串值（SQLite不支持enum类型）
            if isinstance(holiday_type_value, str):
                # 支持直接使用枚举值
                valid_types = ['01', '02', '03']
                if holiday_type_value not in valid_types:
                    raise ValueError(f"无效的节假日类型: {holiday_type_value}")
            # 如果已经是枚举实例，转换为字符串值
            elif hasattr(holiday_type_value, 'value'):
                holiday_dict['holiday_type'] = holiday_type_value.value
        
        holiday = Holiday(**holiday_dict)
        db.add(holiday)
        db.commit()
        db.refresh(holiday)
        return holiday
    
    @staticmethod
    def get_by_id(db: Session, holiday_id: int) -> Optional[Any]:
        """根据ID获取节假日"""
        from .models import Holiday
        return db.query(Holiday).filter(Holiday.id == holiday_id).first()
    
    @staticmethod
    def get_by_date(db: Session, date: Any) -> Optional[Any]:
        """根据日期获取节假日"""
        from .models import Holiday
        return db.query(Holiday).filter(Holiday.date == date).first()
    
    @staticmethod
    def get_list(
        db: Session, 
        page: int = 1, 
        page_size: int = 10, 
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        is_holiday: Optional[bool] = None,
        holiday_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取节假日列表"""
        from .models import Holiday
        from .models import HolidayType
        
        # 构建查询
        query = db.query(Holiday)
        
        # 应用过滤条件
        if start_date:
            query = query.filter(Holiday.date >= start_date)
        if end_date:
            query = query.filter(Holiday.date <= end_date)
        if is_holiday is not None:
            query = query.filter(Holiday.is_holiday == is_holiday)
        if holiday_type:
            try:
                # 验证并使用枚举值进行过滤
                valid_types = ['01', '02', '03']
                if holiday_type in valid_types:
                    query = query.filter(Holiday.holiday_type == holiday_type)
                elif hasattr(HolidayType, holiday_type.upper()):
                    # 尝试从枚举名称获取枚举实例
                    holiday_type_enum = getattr(HolidayType, holiday_type.upper())
                    query = query.filter(Holiday.holiday_type == holiday_type_enum.value)
            except Exception:
                pass
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        items = query.order_by(Holiday.date.desc()).offset(offset).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    def update(db: Session, holiday_id: int, holiday_update: Any) -> Optional[Any]:
        """更新节假日"""
        from .models import Holiday
        
        # 获取记录
        holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
        if not holiday:
            return None
        
        # 更新字段
        update_data = holiday_update.model_dump(exclude_unset=True)
        
        # 特殊处理holiday_type枚举值转换
        if update_data.get('holiday_type'):
            holiday_type_value = update_data['holiday_type']
            
            # 如果是字符串，验证并保持字符串值
            if isinstance(holiday_type_value, str):
                valid_types = ['01', '02', '03']
                if holiday_type_value not in valid_types:
                    raise ValueError(f"无效的节假日类型: {holiday_type_value}")
            # 如果已经是枚举实例，转换为字符串值
            elif hasattr(holiday_type_value, 'value'):
                update_data['holiday_type'] = holiday_type_value.value
        
        for field, value in update_data.items():
            setattr(holiday, field, value)
        
        db.commit()
        db.refresh(holiday)
        return holiday
    
    @staticmethod
    def delete(db: Session, holiday_id: int) -> bool:
        """删除节假日"""
        from .models import Holiday
        
        # 获取记录
        holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
        if not holiday:
            return False
        
        # 删除记录
        db.delete(holiday)
        db.commit()
        return True
    
    @staticmethod
    def batch_create(db: Session, holidays: List[Any]) -> Dict[str, Any]:
        """批量创建节假日"""
        from .models import Holiday
        
        success_count = 0
        failed_count = 0
        failed_details = []
        
        for idx, holiday_data in enumerate(holidays):
            try:
                # 检查日期是否已存在
                existing = db.query(Holiday).filter(Holiday.date == holiday_data.date).first()
                if existing:
                    failed_count += 1
                    failed_details.append({
                        "index": idx,
                        "date": str(holiday_data.date),
                        "error": "日期已存在"
                    })
                    continue
                
                # 创建记录
                holiday_dict = holiday_data.model_dump()
                
                # 特殊处理holiday_type枚举值转换
                if holiday_dict.get('holiday_type'):
                    holiday_type_value = holiday_dict['holiday_type']
                    
                    # 如果是字符串，验证并保持字符串值
                    if isinstance(holiday_type_value, str):
                        valid_types = ['01', '02', '03']
                        if holiday_type_value not in valid_types:
                            raise ValueError(f"无效的节假日类型: {holiday_type_value}")
                    # 如果已经是枚举实例，转换为字符串值
                    elif hasattr(holiday_type_value, 'value'):
                        holiday_dict['holiday_type'] = holiday_type_value.value
                
                holiday = Holiday(**holiday_dict)
                db.add(holiday)
                success_count += 1
                
                # 每50条提交一次
                if success_count % 50 == 0:
                    db.flush()
                    
            except Exception as e:
                failed_count += 1
                failed_details.append({
                    "index": idx,
                    "date": str(holiday_data.date),
                    "error": str(e)
                })
        
        # 提交事务
        db.commit()
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_details": failed_details
        }


# 创建CRUD实例
holiday_crud = HolidayCRUD()
