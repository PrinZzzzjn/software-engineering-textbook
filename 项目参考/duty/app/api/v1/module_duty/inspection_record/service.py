from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.exceptions import BadRequestException
from app.api.v1.module_duty.inspection_record.crud import InspectionRecordCRUD
from app.api.v1.module_duty.inspection_record.schema import InspectionRecordCreate, InspectionRecordUpdate
from app.api.v1.module_duty.personnel.crud import PersonnelCRUD
from app.api.v1.module_duty.duty_record.crud import DutyRecordCRUD
from app.core.database import get_db
from app.core.database import SessionLocal
from sqlalchemy.orm import Session

def get_current_user_sync(db: Session, username: str):
    """同步获取用户信息的辅助函数"""
    # 这里可以根据实际情况从数据库获取用户信息
    # 暂时返回一个模拟的用户对象
    return {'certificate_number': username, 'username': username}

class InspectionRecordService:
    """查班记录服务类"""
    
    def __init__(self):
        """初始化服务类"""
        self.db = next(get_db())
        self.inspection_record_crud = InspectionRecordCRUD(self.db)
        self.personnel_crud = PersonnelCRUD()
        self.duty_record_crud = DutyRecordCRUD(self.db)
    
    def get_inspection_record_list(
        self,
        page: int = 1,
        page_size: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        inspector_certificate_number: Optional[str] = None,
        duty_record_id: Optional[int] = None,
        inspection_type: Optional[str] = None,
        evaluation_level: Optional[str] = None,
        sort_by: str = "create_time",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """获取查班记录列表"""
        # 验证分页参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # 验证时间参数
        if start_date and end_date and start_date > end_date:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 验证排序参数
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        
        # 查询数据
        items, total = self.inspection_record_crud.get_multi(
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
            inspector_certificate_number=inspector_certificate_number,
            duty_record_id=duty_record_id,
            inspection_type=inspection_type,
            evaluation_level=evaluation_level,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # 计算总页数
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages
        }
    
    def get_inspection_record_by_id(self, id: int) -> Dict[str, Any]:
        """根据ID获取查班记录详情"""
        # 查询查班记录
        inspection_record = self.inspection_record_crud.get_by_id(id)
        if not inspection_record:
            raise BadRequestException("查班记录不存在")
        
        # 构建响应数据
        result = inspection_record.__dict__.copy()
        result.pop('_sa_instance_state', None)
        
        # 添加关联信息
        if inspection_record.inspector:
            result['inspector_name'] = inspection_record.inspector.name
        
        result['inspection_type_text'] = inspection_record.get_inspection_type_text()
        result['evaluation_level_text'] = inspection_record.get_evaluation_level_text()
        
        # 添加值班信息
        if inspection_record.duty_record:
            duty_info = {
                'start_time': inspection_record.duty_record.start_time,
                'end_time': inspection_record.duty_record.end_time,
                'workstation_id': inspection_record.duty_record.workstation_id,
                'personnel_certificate_number': inspection_record.duty_record.personnel_certificate_number,
                'personnel_name': inspection_record.duty_record.personnel.name if inspection_record.duty_record.personnel else None
            }
            result['duty_info'] = duty_info
        
        return result
    
    def create_inspection_record(self, inspection_record_data: InspectionRecordCreate, current_user: str) -> Dict[str, Any]:
        """创建查班记录"""
        # 验证当前用户
        user_info = get_current_user_sync(self.db, current_user)
        if not user_info:
            raise BadRequestException("用户未登录")
        
        # 获取查班人员证件号（当前用户）
        inspector_cert = user_info.get('certificate_number') or user_info.get('username')
        
        # 验证值班记录是否存在
        if not self.inspection_record_crud.check_duty_record_exists(inspection_record_data.duty_record_id):
            raise BadRequestException("值班记录不存在")
        
        # 验证时间参数
        if inspection_record_data.start_time >= inspection_record_data.end_time:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 创建记录
        try:
            # 添加查班人员信息
            create_data = inspection_record_data.model_dump()
            create_data['inspector_certificate_number'] = inspector_cert
            
            # 创建记录
            inspection_record = self.inspection_record_crud.create(db=self.db, obj_in=create_data)
            
            # 重新查询以获取完整信息
            return self.get_inspection_record_by_id(inspection_record.id)
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"创建查班记录失败: {str(e)}")
    
    def update_inspection_record(self, id: int, inspection_record_data: InspectionRecordUpdate) -> Dict[str, Any]:
        """更新查班记录"""
        # 检查记录是否存在
        inspection_record = self.inspection_record_crud.get_by_id(id)
        if not inspection_record:
            raise BadRequestException("查班记录不存在")
        
        # 验证时间参数
        if inspection_record_data.start_time and inspection_record_data.end_time and inspection_record_data.start_time >= inspection_record_data.end_time:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 更新记录
        try:
            inspection_record = self.inspection_record_crud.update(db=self.db, db_obj=inspection_record, obj_in=inspection_record_data)
            return self.get_inspection_record_by_id(inspection_record.id)
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"更新查班记录失败: {str(e)}")
    
    def delete_inspection_record(self, id: int) -> Dict[str, str]:
        """删除查班记录"""
        # 检查记录是否存在
        inspection_record = self.inspection_record_crud.get_by_id(id)
        if not inspection_record:
            raise BadRequestException("查班记录不存在")
        
        # 删除记录
        try:
            self.inspection_record_crud.delete(db=self.db, id=id)
            return {"message": "查班记录删除成功"}
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"删除查班记录失败: {str(e)}")
    
    def get_inspection_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取查班统计信息"""
        # 验证时间参数
        if start_date and end_date and start_date > end_date:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 获取统计数据
        return self.inspection_record_crud.get_statistics(start_date, end_date)
    
    def get_by_duty_record_id(self, duty_record_id: int) -> List[Dict[str, Any]]:
        """根据值班记录ID获取查班记录列表"""
        inspection_records = self.inspection_record_crud.get_by_duty_record_id(duty_record_id)
        
        # 格式化结果
        results = []
        for record in inspection_records:
            result = record.__dict__.copy()
            result.pop('_sa_instance_state', None)
            result['inspection_type_text'] = record.get_inspection_type_text()
            result['evaluation_level_text'] = record.get_evaluation_level_text()
            results.append(result)
        
        return results