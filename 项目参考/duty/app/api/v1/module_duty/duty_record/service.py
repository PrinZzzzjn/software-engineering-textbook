from typing import Optional, Dict, Any, List
from datetime import datetime, date
from app.core.exceptions import BadRequestException
from app.api.v1.module_duty.duty_record.crud import DutyRecordCRUD
from app.api.v1.module_duty.duty_record.schema import DutyRecordCreate, DutyRecordUpdate
from app.api.v1.module_duty.personnel.crud import PersonnelCRUD
from app.api.v1.module_duty.workstation.crud import WorkstationCRUD
from app.core.database import get_db

class DutyRecordService:
    """值班记录服务类"""
    
    def __init__(self):
        """初始化服务类"""
        self.db = next(get_db())
        self.duty_record_crud = DutyRecordCRUD(self.db)
        self.personnel_crud = PersonnelCRUD()
        self.workstation_crud = WorkstationCRUD()
    
    def get_duty_record_list(
        self,
        page: int = 1,
        page_size: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        personnel_certificate_number: Optional[str] = None,
        workstation_id: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """获取值班记录列表"""
        # 验证分页参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # 验证时间参数
        if start_time and end_time and start_time > end_time:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 验证排序参数
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        
        # 查询数据
        items, total = self.duty_record_crud.get_multi(
            page=page,
            page_size=page_size,
            start_time=start_time,
            end_time=end_time,
            personnel_certificate_number=personnel_certificate_number,
            workstation_id=workstation_id,
            status=status,
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
    
    def get_duty_record_by_id(self, id: int) -> Dict[str, Any]:
        """根据ID获取值班记录详情"""
        # 查询值班记录
        duty_record = self.duty_record_crud.get_by_id(id)
        if not duty_record:
            raise BadRequestException("值班记录不存在")
        
        # 构建响应数据
        result = duty_record.__dict__.copy()
        result.pop('_sa_instance_state', None)
        
        # 添加关联信息
        if duty_record.personnel:
            result['personnel_name'] = duty_record.personnel.name
            result['personnel_info'] = {
                'position': duty_record.personnel.position,
                'department': duty_record.personnel.department.full_name if duty_record.personnel.department else None
            }
        
        if duty_record.successor:
            result['successor_name'] = duty_record.successor.name
        
        if duty_record.workstation:
            result['workstation_name'] = duty_record.workstation.workstation_name
        
        # 这里可以添加查班记录等关联信息
        result['inspection_records'] = []
        
        return result
    
    def create_duty_record(self, duty_record_data: DutyRecordCreate) -> Dict[str, Any]:
        """创建值班记录"""
        # 验证人员是否存在
        personnel = self.personnel_crud.get_by_certificate_number(self.db, duty_record_data.personnel_certificate_number)
        if not personnel:
            raise BadRequestException("值班人员不存在")
        
        # 验证接班人员是否存在（如果提供）
        if duty_record_data.successor_certificate_number:
            successor = self.personnel_crud.get_by_certificate_number(self.db, duty_record_data.successor_certificate_number)
            if not successor:
                raise BadRequestException("接班人员不存在")
        
        # 验证工作地点是否存在（如果提供）
        if duty_record_data.workstation_id:
            workstation = self.workstation_crud.get_by_workstation_id(self.db, duty_record_data.workstation_id)
            if not workstation:
                raise BadRequestException("工作地点不存在")
        
        # 验证时间参数
        if duty_record_data.start_time >= duty_record_data.end_time:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 检查时间冲突
        if self.duty_record_crud.check_time_conflict(
            duty_record_data.personnel_certificate_number,
            duty_record_data.start_time,
            duty_record_data.end_time
        ):
            raise BadRequestException("该时间段已存在值班记录")
        
        # 创建记录
        try:
            # 设置创建人
            if not duty_record_data.created_by:
                duty_record_data.created_by = "system"
            
            duty_record = self.duty_record_crud.create(db=self.db, obj_in=duty_record_data)
            
            # 重新查询以获取完整信息
            return self.get_duty_record_by_id(duty_record.id)
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"创建值班记录失败: {str(e)}")
    
    def update_duty_record(self, id: int, duty_record_data: DutyRecordUpdate) -> Dict[str, Any]:
        """更新值班记录"""
        # 检查记录是否存在
        duty_record = self.duty_record_crud.get_by_id(id)
        if not duty_record:
            raise BadRequestException("值班记录不存在")
        
        # 验证接班人员是否存在（如果提供）
        if duty_record_data.successor_certificate_number is not None:
            if duty_record_data.successor_certificate_number:
                successor = self.personnel_crud.get_by_certificate_number(self.db, duty_record_data.successor_certificate_number)
                if not successor:
                    raise BadRequestException("接班人员不存在")
        
        # 验证工作地点是否存在（如果提供）
        if duty_record_data.workstation_id is not None:
            if duty_record_data.workstation_id:
                workstation = self.workstation_crud.get_by_workstation_id(self.db, duty_record_data.workstation_id)
                if not workstation:
                    raise BadRequestException("工作地点不存在")
        
        # 验证时间参数
        start_time = duty_record_data.start_time or duty_record.start_time
        end_time = duty_record_data.end_time or duty_record.end_time
        
        if start_time >= end_time:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 检查时间冲突（排除当前记录）
        personnel_cert = duty_record.personnel_certificate_number
        if self.duty_record_crud.check_time_conflict(
            personnel_cert,
            start_time,
            end_time,
            exclude_id=id
        ):
            raise BadRequestException("该时间段已存在值班记录")
        
        # 更新记录
        try:
            duty_record = self.duty_record_crud.update(db=self.db, db_obj=duty_record, obj_in=duty_record_data)
            return self.get_duty_record_by_id(duty_record.id)
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"更新值班记录失败: {str(e)}")
    
    def delete_duty_record(self, id: int) -> Dict[str, str]:
        """删除值班记录"""
        # 检查记录是否存在
        duty_record = self.duty_record_crud.get_by_id(id)
        if not duty_record:
            raise BadRequestException("值班记录不存在")
        
        # 删除记录
        try:
            self.duty_record_crud.delete(db=self.db, id=id)
            return {"message": "值班记录删除成功"}
        except Exception as e:
            self.db.rollback()
            raise BadRequestException(f"删除值班记录失败: {str(e)}")
    
    def get_duty_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取值班统计信息"""
        # 验证时间参数
        if start_time and end_time and start_time > end_time:
            raise BadRequestException("开始时间必须早于结束时间")
        
        # 获取统计数据
        return self.duty_record_crud.get_statistics(start_time, end_time)
