from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_db, get_current_user
from .service import AnalyticsService
from .schema import StaffDutyYearly, DutyTimeDistribution, WorkstationDutyYearly, ContributionRanking, HolidayDutyStat, ExtremeWeatherDutyStat, WeatherExtremeStats

router = APIRouter()


@router.get("/staff-duty-yearly", response_model=StaffDutyYearly,summary="统计指定人员在特定年份的值班情况")
def get_staff_duty_yearly(
    personnel_certificate_number: str = Query(..., description="人员证件号"),
    year: str = Query(..., description="年份（格式：YYYY）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统计指定人员在特定年份的值班情况
    
    - **personnel_certificate_number**: 人员证件号（必填）
    - **year**: 年份（必填，格式：YYYY）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误，请使用YYYY格式")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_staff_duty_yearly(
            db=db,
            personnel_certificate_number=personnel_certificate_number,
            year=year
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/extreme-weather-duty", response_model=ExtremeWeatherDutyStat,summary="统计指定人员在特定年份的极端天气值班记录")
def get_extreme_weather_duty_stat(
    personnel_certificate_number: str = Query(..., description="人员证件号", alias="personnel_id"),
    year: str = Query(..., description="年份（格式：YYYY）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统计指定人员在特定年份的极端天气值班记录
    
    极端天气定义：炎热、酷热、严寒、极寒、大雨、暴雨、暴雪、大雪、大风、烈风
    
    - **personnel_certificate_number**: 人员证件号（必填，可使用personnel_id别名）
    - **year**: 年份（必填，格式：YYYY）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误，请使用YYYY格式")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_extreme_weather_duty_stat(
            db=db,
            personnel_certificate_number=personnel_certificate_number,
            year=year
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取极端天气值班统计失败")


@router.get("/holiday-duty", response_model=HolidayDutyStat,summary="统计指定人员在特定年份的节假日值班记录")
def get_holiday_duty_stat(
    year: str = Query(..., description="年份（必填，格式：YYYY）"),
    personnel_certificate_number: str = Query(..., description="人员证件号（必填）"),
    page: int = Query(1, description="页码（默认1）"),
    page_size: int = Query(10, description="每页数量（默认10）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统计今年内的执勤记录中，在节假日执勤的记录
    
    - **year**: 年份（必填，格式：YYYY）
    - **personnel_certificate_number**: 人员证件号（必填）
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认10）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_holiday_duty_stat(
            db=db,
            personnel_certificate_number=personnel_certificate_number,
            year=year,
            page=page,
            page_size=page_size
        )
        
        return result
    except ValueError as e:
        if str(e) == "人员不存在":
            raise HTTPException(status_code=400, detail="人员不存在")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/contribution-ranking", response_model=ContributionRanking,summary="计算指定人员在特定年份值班时长在团队中的贡献度和排名")
def get_contribution_ranking(
    personnel_certificate_number: str = Query(..., description="人员证件号"),
    year: str = Query(..., description="年份（格式：YYYY）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    计算指定人员在特定年份值班时长在团队中的贡献度和排名
    
    - **personnel_certificate_number**: 人员证件号（必填）
    - **year**: 年份（必填，格式：YYYY）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误，请使用YYYY格式")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_contribution_ranking(
            db=db,
            personnel_certificate_number=personnel_certificate_number,
            year=year
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/duty-time-distribution", response_model=DutyTimeDistribution,summary="统计指定人员在特定年份的值班时间段分布")
def get_duty_time_distribution(
    personnel_certificate_number: str = Query(..., description="人员证件号"),
    year: str = Query(..., description="年份（格式：YYYY）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统计指定人员在特定年份的值班时间段分布
    
    - **personnel_certificate_number**: 人员证件号（必填）
    - **year**: 年份（必填，格式：YYYY）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误，请使用YYYY格式")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_duty_time_distribution(
            db=db,
            personnel_certificate_number=personnel_certificate_number,
            year=year
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/weather-extreme-stats", response_model=WeatherExtremeStats,summary="统计指定人员在特定年份值班记录中的天气极值")
def get_weather_extreme_stats(
    personnel_certificate_number: str = Query(..., description="人员证件号"),
    year: str = Query(..., description="年份（格式：YYYY）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统计指定人员在特定年份值班记录中的天气极值
    
    - **personnel_certificate_number**: 人员证件号（必填）
    - **year**: 年份（必填，格式：YYYY）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误，请使用YYYY格式")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_weather_extreme_stats(
            db=db,
            personnel_certificate_number=personnel_certificate_number,
            year=year
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/workstation-duty-yearly", response_model=WorkstationDutyYearly,summary="统计指定工位在特定年份的值班情况")
def get_workstation_duty_yearly(
    workstation_id: str = Query(..., description="工位ID"),
    year: str = Query(..., description="年份（格式：YYYY）"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统计指定工位在特定年份的值班情况
    
    - **workstation_id**: 工位ID（必填）
    - **year**: 年份（必填，格式：YYYY）
    """
    try:
        # 验证年份格式
        if len(year) != 4 or not year.isdigit():
            raise HTTPException(status_code=400, detail="年份格式错误，请使用YYYY格式")
        
        # 调用服务层获取统计数据
        result = AnalyticsService.get_workstation_duty_yearly(
            db=db,
            workstation_id=workstation_id,
            year=year
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
