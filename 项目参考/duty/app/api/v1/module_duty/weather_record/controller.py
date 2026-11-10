from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.api.v1.module_duty.weather_record.schemas import WeatherRecordCreate, WeatherRecordUpdate, WeatherRecordResponse, ImportResponse, ImportFailedRecord
from app.api.v1.module_duty.weather_record.param import WeatherRecordQueryParams, WeatherRecordDeleteByDeptParams
from app.api.v1.module_duty.weather_record.service import weather_record_service
from app.core.dependencies import get_db, get_current_user, get_current_admin_user
from app.core.exceptions import NotFoundException
import asyncio
import traceback
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/weather-records", tags=["天气记录管理"])

@router.post("", response_model=WeatherRecordResponse, summary="创建天气记录")
async def create_weather_record(
    record_data: WeatherRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """创建单条天气记录"""
    try:
        # 调用service创建记录
        record = weather_record_service.create_record(db, record_data)
        return record

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=Dict[str, Any], summary="获取天气记录列表")
async def get_weather_records_list(
    params: WeatherRecordQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取天气记录列表，支持分页和多种筛选条件"""
    try:
        # 调用service获取列表
        result = weather_record_service.get_records_list(db, params)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=WeatherRecordResponse, summary="获取天气记录详情")
async def get_weather_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """根据ID获取天气记录详情"""
    try:
        # 调用service获取记录
        record = weather_record_service.get_record_by_id(db, id)
        return record
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=WeatherRecordResponse, summary="更新天气记录")
async def update_weather_record(
    id: int,
    update_data: WeatherRecordUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """更新天气记录"""
    try:
        # 调用service更新记录
        record = weather_record_service.update_record(db, id, update_data)
        return record
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}", response_model=Dict[str, Any], summary="删除天气记录")
async def delete_weather_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """删除天气记录"""
    try:
        # 调用service删除记录
        weather_record_service.delete_record(db, id)
        return {"message": "天气记录删除成功"}
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/by-dept/", response_model=Dict[str, Any], summary="按部门代码删除天气记录")
async def delete_records_by_dept(
    dept_code: str = Query(..., description="部门代码"),
    start_time: Optional[str] = Query(None, description="开始时间，格式：YYYY-MM-DD HH:MM:SS"),
    end_time: Optional[str] = Query(None, description="结束时间，格式：YYYY-MM-DD HH:MM:SS"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """按工作站ID删除天气记录，可选择时间范围"""
    try:
        # 转换时间字符串为datetime对象
        parsed_start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else None
        parsed_end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else None
        
        # 构建参数对象
        params = WeatherRecordDeleteByDeptParams(
            dept_code=dept_code,
            start_time=parsed_start_time,
            end_time=parsed_end_time
        )
        
        # 调用服务层方法删除记录
        result = weather_record_service.delete_records_by_dept_code(db, params)
        
        logger.info(f"删除部门 {dept_code} 的天气记录完成")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"时间格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import", response_model=ImportResponse, summary="批量导入天气记录")
async def batch_import_weather_records(
    file: UploadFile = File(..., description="Excel文件，格式为.xlsx或.xls"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """批量导入天气记录，支持Excel数据导入，优化大文件处理能力"""
    try:
        import pandas as pd
        import io
        import json
        from datetime import datetime
        from app.api.v1.module_duty.weather_record.model import WeatherRecord
        
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="只支持.xlsx或.xls格式的文件")
        
        # 读取Excel文件
        contents = await file.read()
        
        # 使用BytesIO处理文件内容
        excel_file = io.BytesIO(contents)
        
        # 读取整个Excel文件，包括元数据
        xl = pd.ExcelFile(excel_file)
        sheet_name = xl.sheet_names[0]  # 假设使用第一个sheet
        
        # 先读取A2和B2单元格中的经纬度信息
        # 使用header=None确保不把第一行当作表头
        meta_df = pd.read_excel(xl, sheet_name=sheet_name, header=None, nrows=2)
        
        # 从A2和B2获取经纬度 (索引从0开始)
        try:
            # A2是纬度，B2是经度，这里调整顺序以正确读取
            latitude = float(meta_df.iloc[1, 0])   # A2单元格 (行索引1, 列索引0)
            longitude = float(meta_df.iloc[1, 1])  # B2单元格 (行索引1, 列索引1)
            
            # 验证经纬度范围
            if not (-180 <= longitude <= 180) or not (-90 <= latitude <= 90):
                raise ValueError(f"经纬度值超出有效范围: 经度={longitude}, 纬度={latitude}")
            
            logger.info(f"从Excel中读取到经纬度信息: 经度={longitude}, 纬度={latitude}")
        except (ValueError, TypeError, IndexError) as e:
            raise ValueError(f"无法从A2和B2单元格读取有效的经纬度信息: {str(e)}")
        
        # 从第四行开始读取实际的数据（skiprows=3表示跳过前3行）
        df = pd.read_excel(xl, sheet_name=sheet_name, skiprows=3)
        
        # 检查导入数据数量
        if df.empty:
            raise ValueError("导入数据不能为空")
        
        if len(df) > 9000:
            raise ValueError("单次导入数据不能超过9000条")
        
        # 导入必要的模块用于计算距离
        import math
        from app.api.v1.module_duty.dept.model import Department
        
        # 获取所有部门信息用于距离计算
        departments = db.query(Department).all()
        if not departments:
            raise HTTPException(status_code=400, detail="系统中未找到任何部门信息，无法匹配最近部门")
        
        # 数据映射：将Excel列名映射到我们的数据模型字段
        column_mapping = {
            'time': 'record_time',
            'temperature_2m (°C)': 'temperature',
            'rain (mm)': 'rainfall',
            'snowfall (cm)': 'snowfall',
            'windspeed_10m (m/s)': 'wind_speed',
            'relativehumidity_2m (%)': 'humidity',
            'longitude': 'longitude',  # 新增经纬度字段
            'latitude': 'latitude'
        }
        
        # 检查必需的基本列是否存在
        basic_required_columns = ['time', 'temperature_2m (°C)', 'rain (mm)', 'snowfall (cm)', 'windspeed_10m (m/s)', 'relativehumidity_2m (%)']
        
        # 检查基本列
        missing_basic_columns = [col for col in basic_required_columns if col not in df.columns]
        if missing_basic_columns:
            raise ValueError(f"Excel文件缺少必要的基本列: {', '.join(missing_basic_columns)}")
        
        # 转换数据
        records = []
        valid_records = []  # 存储有效的记录
        logger.info(f"开始处理天气记录导入，共{len(df)}条数据，将自动匹配最近部门")
        
        # 先预处理所有记录，检查格式并收集时间点
        record_time_set = set()  # 用于检测同一文件内的重复记录
        
        for idx, row in df.iterrows():
            try:
                # 处理record_time，支持多种格式
                record_time = row['time']
                # 确保转换为datetime对象，处理pandas的Timestamp类型
                if hasattr(record_time, 'to_pydatetime'):
                    # 处理pandas的Timestamp对象
                    record_time = record_time.to_pydatetime()
                elif isinstance(record_time, str):
                    try:
                        record_time = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            record_time = datetime.strptime(record_time, '%Y-%m-%d %H:%M')
                        except ValueError:
                            try:
                                record_time = datetime.strptime(record_time, '%Y-%m-%d')
                            except ValueError:
                                raise ValueError(f"日期时间格式错误: {record_time}")
                elif isinstance(record_time, (int, float)):
                    # 处理Excel中的数字格式日期
                    try:
                        from datetime import timedelta
                        # Excel的基准日期是1900-01-01
                        record_time = datetime(1899, 12, 30) + timedelta(days=record_time)
                    except:
                        raise ValueError(f"无法解析的日期数字: {record_time}")
                
                # 使用从A2和B2获取的经纬度信息，不需要每行都有经纬度
                # 经纬度已经在文件开头验证过，这里直接使用全局变量
                
                # 使用Haversine公式计算距离并找到最近的部门
                def calculate_distance(lat1, lon1, lat2, lon2):
                    # 将经纬度转换为弧度
                    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                    # Haversine公式
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    r = 6371  # 地球半径，单位为公里
                    return c * r
                
                # 计算与所有部门的距离并找到最近的
                nearest_dept = None
                min_distance = float('inf')
                
                for dept in departments:
                    if dept.longitude is None or dept.latitude is None:
                        continue  # 跳过没有地理信息的部门
                    
                    distance = calculate_distance(latitude, longitude, dept.latitude, dept.longitude)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_dept = dept
                
                if not nearest_dept:
                    raise ValueError(f"未找到可用的部门地理信息")
                
                dept_code = nearest_dept.dept_code
                
                # 检查同一文件内的重复记录
                # 使用字符串表示作为键，避免datetime比较问题
                time_str = record_time.isoformat()
                time_dept_key = (time_str, dept_code)
                if time_dept_key in record_time_set:
                    records.append({
                        'row': idx + 2,
                        'error': f"第{idx + 2}行数据错误: 文件内存在相同时间点和部门的记录"
                    })
                    continue
                record_time_set.add(time_dept_key)
                
                # 获取天气数据
                temperature = float(row['temperature_2m (°C)'])
                rainfall = float(row['rain (mm)'])
                snowfall = float(row['snowfall (cm)'])
                wind_speed = float(row['windspeed_10m (m/s)'])
                humidity = float(row['relativehumidity_2m (%)'])
                
                # 计算天气状况
                weather_conditions = WeatherRecord.calculate_weather_conditions(
                    temperature, humidity, rainfall, snowfall, wind_speed
                )
                
                # 构建记录，不包含row字段
                record = {
                    'record_time': record_time,
                    'dept_code': dept_code,
                    'temperature': temperature,
                    'rainfall': rainfall,
                    'snowfall': snowfall,
                    'wind_speed': wind_speed,
                    'humidity': humidity,
                    'weather_conditions': json.dumps(weather_conditions)  # 存储为JSON字符串
                }
                # 保存行号信息，用于后续错误报告
                record['_row'] = idx + 2  # 使用下划线前缀避免与模型字段冲突
                records.append(record)
                valid_records.append(record)
            except Exception as e:
                records.append({
                    'row': idx + 2,
                    'error': f"第{idx + 2}行数据格式错误: {str(e)}"
                })
        
        logger.info(f"数据预处理完成，有效记录: {len(valid_records)}, 格式错误: {len(records) - len(valid_records)}")
        
        # 直接处理所有数据
        logger.info(f"开始导入天气记录，共{len(records)}条数据")
        result = weather_record_service.batch_import_records(db, records)
        
        all_success_count = result['success_count']
        all_failed_count = result['failed_count']
        all_failed_details = result.get('failed_details', [])
        
        # 构建响应数据
        failed_records = [
            ImportFailedRecord(row=item.get("row", 0), error=item.get("error", "未知错误"))
            for item in all_failed_details
        ]
        
        response_data = ImportResponse(
            message=f"导入完成，成功{all_success_count}条，失败{all_failed_count}条",
            success_count=all_success_count,
            failed_count=all_failed_count,
            failed_records=failed_records
        )
        
        logger.info(f"天气记录导入完成，成功{all_success_count}条，失败{all_failed_count}条")
        return response_data

    except pd.errors.EmptyDataError:
        logger.error("Excel文件为空或格式不正确")
        raise HTTPException(status_code=400, detail="Excel文件为空或格式不正确")
    except ValueError as e:
        logger.error(f"导入参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"导入失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        await file.close()
