# 节假日服务层 - 使用局部导入避免循环依赖
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, date
import pandas as pd
import io


class HolidayService:
    """节假日服务类"""
    
    @staticmethod
    def create_holiday(db: Session, holiday_data: Any) -> Any:
        """创建节假日"""
        from .crud import holiday_crud
        return holiday_crud.create(db, holiday_data)
    
    @staticmethod
    def get_holiday_by_id(db: Session, holiday_id: int) -> Any:
        """根据ID获取节假日"""
        from .crud import holiday_crud
        return holiday_crud.get_by_id(db, holiday_id)
    
    @staticmethod
    def get_holiday_list(
        db: Session, 
        page: int = 1, 
        page_size: int = 10, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_holiday: Optional[bool] = None,
        holiday_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取节假日列表"""
        from .crud import holiday_crud
        return holiday_crud.get_list(
            db=db,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
            is_holiday=is_holiday,
            holiday_type=holiday_type
        )
    
    @staticmethod
    def update_holiday(db: Session, holiday_id: int, holiday_update: Any) -> Any:
        """更新节假日"""
        from .crud import holiday_crud
        return holiday_crud.update(db, holiday_id, holiday_update)
    
    @staticmethod
    def delete_holiday(db: Session, holiday_id: int) -> bool:
        """删除节假日"""
        from .crud import holiday_crud
        return holiday_crud.delete(db, holiday_id)
    
    @staticmethod
    def check_holiday(db: Session, date_str: str) -> Dict[str, Any]:
        """检查日期是否为节假日"""
        # 解析日期
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("日期格式不正确，请使用YYYY-MM-DD格式")
        
        # 查询数据库
        from .crud import holiday_crud
        holiday = holiday_crud.get_by_date(db, check_date)
        
        if holiday:
            # 从数据库获取的节假日信息
            holiday_info = {
                "id": holiday.id,
                "name": holiday.name,
                "type": holiday.holiday_type if holiday.holiday_type else None,
                "description": holiday.description
            }
            is_holiday = holiday.is_holiday
        else:
            # 检查是否为周末（周六、周日）
            is_holiday = check_date.weekday() in [5, 6]
            holiday_info = {
                "name": "周末" if is_holiday else "工作日",
                "type": "02" if is_holiday else None
            }
        
        # 构建响应
        from .schemas import HolidayCheckResponse
        return HolidayCheckResponse(
            date=date_str,
            is_holiday=is_holiday,
            holiday_info=holiday_info if holiday_info else None
        )
    
    @staticmethod
    def import_holidays_from_excel(db: Session, file_content: bytes) -> Dict[str, Any]:
        """从Excel导入节假日"""
        # 解析Excel文件
        try:
            df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Excel文件解析失败: {str(e)}")
        
        # 验证必要的列
        required_columns = ['date']
        missing_columns = [col for col in required_columns if col.lower() not in df.columns.str.lower()]
        if missing_columns:
            raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
        
        # 准备导入数据
        holidays_to_create = []
        from .schemas import HolidayCreate
        from .models import HolidayType
        
        for idx, row in df.iterrows():
            try:
                # 获取日期
                if pd.isna(row.get('date')):
                    continue
                
                holiday_date = pd.to_datetime(row['date']).date()
                
                # 创建HolidayCreate对象
                holiday_data = HolidayCreate(
                    date=holiday_date,
                    is_holiday=row.get('is_holiday', True) if not pd.isna(row.get('is_holiday')) else True,
                    name=row.get('name') if not pd.isna(row.get('name')) else None,
                    description=row.get('description') if not pd.isna(row.get('description')) else None
                )
                
                # 处理节假日类型
                holiday_type = row.get('holiday_type')
                if holiday_type and not pd.isna(holiday_type):
                    holiday_type_str = str(holiday_type).strip().upper()
                    if holiday_type_str in HolidayType.__members__:
                        holiday_data.holiday_type = HolidayType[holiday_type_str]
                
                holidays_to_create.append(holiday_data)
                
            except Exception as e:
                raise ValueError(f"第{idx + 2}行数据解析失败: {str(e)}")
        
        # 批量创建
        from .crud import holiday_crud
        result = holiday_crud.batch_create(db, holidays_to_create)
        
        # 转换为ImportResult
        from .schemas import ImportResult
        return ImportResult(**result)


# 创建服务实例
holiday_service = HolidayService()
