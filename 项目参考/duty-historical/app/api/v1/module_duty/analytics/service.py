from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import List, Dict
from app.api.v1.module_duty.duty_record.model import DutyRecord
from app.api.v1.module_duty.personnel.model import Personnel
from app.api.v1.module_duty.workstation.model import Workstation
from app.api.v1.module_duty.holiday.models import Holiday
from app.api.v1.module_duty.weather_record.model import WeatherRecord
from .schema import StaffDutyYearly, MonthlyDuty, DutyTimeDistribution, HourDistribution, WorkstationDutyYearly, ContributionRanking, HolidayDutyStat, HolidayDutyItem, ExtremeWeatherDutyStat, ExtremeWeatherDutyRecord, WeatherTypeSummary, WeatherExtremeStats, WeatherExtremeValue


class AnalyticsService:
    """数据分析服务类"""
    
    @staticmethod
    def get_duty_time_distribution(db: Session, personnel_certificate_number: str, year: str) -> DutyTimeDistribution:
        """
        统计指定人员在特定年份的值班时间段分布
        
        Args:
            db: 数据库会话
            personnel_certificate_number: 人员证件号
            year: 年份（YYYY格式）
            
        Returns:
            DutyTimeDistribution: 值班时间段分布统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询人员信息
        personnel = db.query(Personnel).filter(
            Personnel.certificate_number == personnel_certificate_number
        ).first()
        
        if not personnel:
            raise ValueError(f"未找到证件号为 {personnel_certificate_number} 的人员")
        
        # 查询该人员该年的所有值班记录
        duty_records = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 初始化24小时的计数器
        hour_counts = {hour: 0 for hour in range(24)}
        
        # 统计每个小时的值班情况
        for record in duty_records:
            start_time = record.start_time
            end_time = record.end_time
            
            # 计算值班记录覆盖的所有小时
            current_hour = start_time.replace(minute=0, second=0, microsecond=0)
            end_hour = end_time.replace(minute=0, second=0, microsecond=0)
            
            if start_time.hour == end_time.hour:
                # 值班记录在同一个小时内
                duration_minutes = (end_time - start_time).total_seconds() / 60
                if duration_minutes >= 30:
                    hour_counts[start_time.hour] += 1
            else:
                # 值班记录跨越多个小时
                # 处理开始小时
                start_hour_end = current_hour + timedelta(hours=1)
                start_duration_minutes = (start_hour_end - start_time).total_seconds() / 60
                if start_duration_minutes >= 30:
                    hour_counts[start_time.hour] += 1
                
                # 处理中间的完整小时
                current_hour += timedelta(hours=1)
                while current_hour < end_hour:
                    hour_counts[current_hour.hour] += 1
                    current_hour += timedelta(hours=1)
                
                # 处理结束小时
                end_duration_minutes = (end_time - end_hour).total_seconds() / 60
                if end_duration_minutes >= 30:
                    hour_counts[end_time.hour] += 1
        
        # 构建小时分布列表
        time_distribution = [HourDistribution(hour=hour, count=count) for hour, count in sorted(hour_counts.items())]
        
        # 找出高峰时段（值班次数最多的小时）
        max_count = max(hour_counts.values()) if hour_counts else 0
        peak_hours = [hour for hour, count in hour_counts.items() if count == max_count]
        peak_hours.sort()  # 按小时顺序排序
        
        # 计算总记录数
        total_records = len(duty_records)
        
        # 构建返回结果
        return DutyTimeDistribution(
            year=year,
            personnel_certificate_number=personnel_certificate_number,
            personnel_name=personnel.name,
            time_distribution=time_distribution,
            peak_hours=peak_hours,
            total_records=total_records
        )
    
    @staticmethod
    def get_staff_duty_yearly(db: Session, personnel_certificate_number: str, year: str) -> StaffDutyYearly:
        """
        统计指定人员在特定年份的值班情况
        
        Args:
            db: 数据库会话
            personnel_certificate_number: 人员证件号
            year: 年份（YYYY格式）
            
        Returns:
            StaffDutyYearly: 年度值班统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询人员信息
        personnel = db.query(Personnel).filter(
            Personnel.certificate_number == personnel_certificate_number
        ).first()
        
        if not personnel:
            raise ValueError(f"未找到证件号为 {personnel_certificate_number} 的人员")
        
        # 查询该人员该年的所有值班记录
        duty_records = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 计算总天数和总小时数，以及月度统计
        total_duty_days = 0
        total_duty_hours = 0
        monthly_stats: Dict[int, Dict[str, int]] = {}
        
        # 初始化12个月的数据
        for month in range(1, 13):
            monthly_stats[month] = {'days': 0, 'hours': 0, 'days_set': set()}
        
        # 计算每个值班记录的时长和天数
        for record in duty_records:
            start_time = record.start_time
            end_time = record.end_time
            month = start_time.month
            
            # 计算时长（小时）
            duration_hours = (end_time - start_time).total_seconds() / 3600
            
            # 计算天数（按自然天计算）
            current_date = start_time.date()
            end_date = end_time.date()
            day_count = 0
            
            while current_date <= end_date:
                monthly_stats[month]['days_set'].add(current_date)
                current_date += timedelta(days=1)
                day_count += 1
            
            # 累计到月度统计
            monthly_stats[month]['hours'] += duration_hours
        
        # 转换月度统计为响应格式
        duty_by_month: List[MonthlyDuty] = []
        for month in range(1, 13):
            days = len(monthly_stats[month]['days_set'])
            hours = round(monthly_stats[month]['hours'])
            
            duty_by_month.append(MonthlyDuty(month=month, days=days, hours=hours))
            
            total_duty_days += days
            total_duty_hours += round(monthly_stats[month]['hours'])
        
        # 构建返回结果
        return StaffDutyYearly(
            personnel_certificate_number=personnel_certificate_number,
            personnel_name=personnel.name,
            year=year,
            total_duty_days=total_duty_days,
            total_duty_hours=total_duty_hours,
            duty_by_month=duty_by_month
        )
    
    @staticmethod
    def get_workstation_duty_yearly(db: Session, workstation_id: str, year: str) -> WorkstationDutyYearly:
        """
        统计指定工位在特定年份的值班情况
        
        Args:
            db: 数据库会话
            workstation_id: 工位ID
            year: 年份（YYYY格式）
            
        Returns:
            WorkstationDutyYearly: 年度值班统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询工位信息
        workstation = db.query(Workstation).filter(
            Workstation.workstation_id == workstation_id
        ).first()
        
        if not workstation:
            raise ValueError(f"未找到ID为 {workstation_id} 的工位")
        
        # 查询该工位该年的所有值班记录
        duty_records = db.query(DutyRecord).filter(
            DutyRecord.workstation_id == workstation_id,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 计算总天数和总小时数，以及月度统计
        total_duty_days = 0
        total_duty_hours = 0
        monthly_stats: Dict[int, Dict[str, int]] = {}
        
        # 初始化12个月的数据
        for month in range(1, 13):
            monthly_stats[month] = {'days': 0, 'hours': 0, 'days_set': set()}
        
        # 计算每个值班记录的时长和天数
        for record in duty_records:
            start_time = record.start_time
            end_time = record.end_time
            month = start_time.month
            
            # 计算时长（小时）
            duration_hours = (end_time - start_time).total_seconds() / 3600
            
            # 计算天数（按自然天计算）
            current_date = start_time.date()
            end_date = end_time.date()
            
            while current_date <= end_date:
                monthly_stats[month]['days_set'].add(current_date)
                current_date += timedelta(days=1)
            
            # 累计到月度统计
            monthly_stats[month]['hours'] += duration_hours
        
        # 转换月度统计为响应格式
        duty_by_month: List[MonthlyDuty] = []
        for month in range(1, 13):
            days = len(monthly_stats[month]['days_set'])
            hours = round(monthly_stats[month]['hours'])
            
            duty_by_month.append(MonthlyDuty(month=month, days=days, hours=hours))
            
            total_duty_days += days
            total_duty_hours += round(monthly_stats[month]['hours'])
        
        # 构建返回结果
        return WorkstationDutyYearly(
            workstation_id=workstation_id,
            workstation_name=workstation.workstation_name,
            year=year,
            total_duty_days=total_duty_days,
            total_duty_hours=total_duty_hours,
            duty_by_month=duty_by_month
        )
    
    @staticmethod
    def get_contribution_ranking(db: Session, personnel_certificate_number: str, year: str) -> ContributionRanking:
        """
        计算指定人员在特定年份值班时长在团队中的贡献度和排名
        
        Args:
            db: 数据库会话
            personnel_certificate_number: 人员证件号
            year: 年份（YYYY格式）
            
        Returns:
            ContributionRanking: 贡献度和排名统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询人员信息
        personnel = db.query(Personnel).filter(
            Personnel.certificate_number == personnel_certificate_number
        ).first()
        
        if not personnel:
            raise ValueError(f"未找到证件号为 {personnel_certificate_number} 的人员")
        
        # 获取人员所属部门
        if not personnel.dept_code:
            raise ValueError(f"人员 {personnel.name} 未分配部门")
        
        department = personnel.department
        if not department:
            raise ValueError(f"未找到部门编码为 {personnel.dept_code} 的部门")
        
        # 统计该人员在指定年份的总值班时长
        user_duty_records = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 计算该人员的总值班小时数
        total_duty_hours = 0.0
        for record in user_duty_records:
            duration_hours = (record.end_time - record.start_time).total_seconds() / 3600
            total_duty_hours += duration_hours
        total_duty_hours = round(total_duty_hours, 2)  # 保留2位小数以确保精确度
        
        # 查询部门下所有人员
        dept_personnel = db.query(Personnel).filter(
            Personnel.dept_code == personnel.dept_code
        ).all()
        
        # 统计部门内每个人员的值班时长
        staff_duty_hours = []
        for staff in dept_personnel:
            staff_records = db.query(DutyRecord).filter(
                DutyRecord.personnel_certificate_number == staff.certificate_number,
                extract('year', DutyRecord.start_time) == year_int
            ).all()
            
            staff_total_hours = 0
            for record in staff_records:
                staff_total_hours += (record.end_time - record.start_time).total_seconds() / 3600
            
            staff_duty_hours.append({
                'certificate_number': staff.certificate_number,
                'hours': staff_total_hours
            })
        
        # 计算部门总值班时长
        dept_total_hour = sum(s['hours'] for s in staff_duty_hours)
        dept_total_hour = round(dept_total_hour, 2)
        
        # 计算部门平均值班时长（只计算有值班记录的人员）
        active_staff_hours = [s['hours'] for s in staff_duty_hours if s['hours'] > 0]
        dept_average_hours = sum(active_staff_hours) / len(active_staff_hours) if active_staff_hours else 0
        dept_average_hours = round(dept_average_hours, 2)
        
        # 计算贡献度
        contribution_rate = total_duty_hours / dept_average_hours if dept_average_hours > 0 else 0
        contribution_rate = round(contribution_rate, 2)
        
        # 计算占部门总值班时长的比例，并以百分比格式表示
        contribution_percentage = f"{round((total_duty_hours / dept_total_hour * 100), 2)}%" if dept_total_hour > 0 else "0%"
        
        # 计算排名（按值班时长降序排序）
        sorted_staff = sorted(staff_duty_hours, key=lambda x: x['hours'], reverse=True)
        ranking = next((i + 1 for i, s in enumerate(sorted_staff) if s['certificate_number'] == personnel_certificate_number), len(sorted_staff))
        
        # 构建返回结果
        return ContributionRanking(
            personnel_certificate_number=personnel_certificate_number,
            personnel_name=personnel.name,
            year=year,
            total_duty_hours=total_duty_hours,
            dept_total_hour=dept_total_hour,
            dept_average_hours=dept_average_hours,
            contribution_rate=contribution_rate,
            contribution_percentage=contribution_percentage,
            ranking=ranking,
            total_staff_count=len(dept_personnel),
            dept_id=department.dept_code,
            dept_name=department.full_name
        )
    
    @staticmethod
    def get_holiday_duty_stat(db: Session, personnel_certificate_number: str, year: str, page: int = 1, page_size: int = 10) -> HolidayDutyStat:
        """
        统计指定人员在特定年份的节假日值班情况
        
        Args:
            db: 数据库会话
            personnel_certificate_number: 人员证件号
            year: 年份（YYYY格式）
            page: 页码
            page_size: 每页数量
            
        Returns:
            HolidayDutyStat: 节假日值班统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询人员信息
        personnel = db.query(Personnel).filter(
            Personnel.certificate_number == personnel_certificate_number
        ).first()
        
        if not personnel:
            raise ValueError("人员不存在")
        
        # 查询该人员在指定年份的所有值班记录
        all_duty_records = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 统计所有值班记录
        total_duty_records = len(all_duty_records)
        
        # 筛选节假日值班记录
        holiday_duty_records = []
        holiday_duty_days_set = set()
        total_holiday_duty_hours = 0.0
        
        for record in all_duty_records:
            # 计算中位时间
            start_time = record.start_time
            end_time = record.end_time
            median_time = start_time + (end_time - start_time) / 2
            median_date = median_time.date()
            
            # 查询是否是节假日
            holiday = db.query(Holiday).filter(
                Holiday.date == median_date,
                Holiday.is_holiday == True
            ).first()
            
            if holiday:
                # 计算值班时长
                duration_hours = (end_time - start_time).total_seconds() / 3600
                total_holiday_duty_hours += duration_hours
                
                # 添加日期到集合（用于统计天数）
                current_date = start_time.date()
                end_date = end_time.date()
                while current_date <= end_date:
                    holiday_duty_days_set.add(current_date)
                    current_date += timedelta(days=1)
                
                # 获取工位信息
                site_name = record.workstation.workstation_name if record.workstation else ""
                
                holiday_duty_records.append({
                    'record': record,
                    'holiday_name': holiday.name or "节假日",
                    'site_name': site_name
                })
        
        # 计算总节假日值班天数
        total_holiday_duty_days = len(holiday_duty_days_set)
        
        # 计算总节假日值班记录数
        total_holiday_records = len(holiday_duty_records)
        
        # 分页处理
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paged_records = holiday_duty_records[start_index:end_index]
        
        # 构建响应项
        items = []
        for item in paged_records:
            record = item['record']
            duty_item = HolidayDutyItem(
                duty_id=str(record.id),  # 假设id是主键
                staff_certificate_number=personnel_certificate_number,
                staff_name=personnel.name,
                start_time=record.start_time,
                end_time=record.end_time,
                holiday_name=item['holiday_name'],
                site_name=item['site_name']
            )
            items.append(duty_item)
        
        # 构建返回结果
        return HolidayDutyStat(
            total=total_holiday_records,
            page=page,
            page_size=page_size,
            year=year,
            total_duty_records=total_duty_records,
            total_holiday_records=total_holiday_records,
            total_holiday_duty_days=total_holiday_duty_days,
            total_holiday_duty_hours=round(total_holiday_duty_hours, 2),
            items=items
        )
    
    @staticmethod
    def get_weather_extreme_stats(db: Session, personnel_certificate_number: str, year: str) -> WeatherExtremeStats:
        """
        统计指定人员在特定年份值班记录中的天气极值
        
        Args:
            db: 数据库会话
            personnel_certificate_number: 人员证件号
            year: 年份（YYYY格式）
            
        Returns:
            WeatherExtremeStats: 天气极值统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询人员信息
        personnel = db.query(Personnel).filter(
            Personnel.certificate_number == personnel_certificate_number
        ).first()
        
        if not personnel:
            raise ValueError(f"未找到证件号为 {personnel_certificate_number} 的人员")
        
        # 查询该人员该年的所有值班记录
        duty_records = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 计算总值班天数和小时数
        total_duty_days = len(set(record.start_time.date() for record in duty_records))
        total_duty_hours = sum(
            (record.end_time - record.start_time).total_seconds() / 3600
            for record in duty_records
        )
        
        # 初始化极值记录
        max_temperature = None
        min_temperature = None
        max_rainfall = None
        max_snowfall = None
        max_wind_speed = None
        
        # 遍历每条值班记录，查找对应的天气记录
        for duty_record in duty_records:
            # 查询值班时间段内的所有天气记录
            # 需要通过部门代码关联，因为WeatherRecord使用dept_code，而DutyRecord通过workstation关联部门
            weather_records = db.query(WeatherRecord).join(
                Workstation, Workstation.dept_code == WeatherRecord.dept_code
            ).filter(
                Workstation.workstation_id == duty_record.workstation_id,
                WeatherRecord.record_time >= duty_record.start_time,
                WeatherRecord.record_time <= duty_record.end_time
            ).all()
            
            # 处理每个天气记录
            for weather_record in weather_records:
                # 更新最高温度
                if max_temperature is None or weather_record.temperature > max_temperature.value:
                    max_temperature = WeatherExtremeValue(
                        value=weather_record.temperature,
                        record_time=weather_record.record_time,
                        duty_id=duty_record.id if hasattr(duty_record, 'id') else None
                    )
                
                # 更新最低温度
                if min_temperature is None or weather_record.temperature < min_temperature.value:
                    min_temperature = WeatherExtremeValue(
                        value=weather_record.temperature,
                        record_time=weather_record.record_time,
                        duty_id=duty_record.id if hasattr(duty_record, 'id') else None
                    )
                
                # 更新最大降雨量
                if max_rainfall is None or weather_record.rainfall > max_rainfall.value:
                    max_rainfall = WeatherExtremeValue(
                        value=weather_record.rainfall,
                        record_time=weather_record.record_time,
                        duty_id=duty_record.id if hasattr(duty_record, 'id') else None
                    )
                
                # 更新最大降雪量
                if max_snowfall is None or weather_record.snowfall > max_snowfall.value:
                    max_snowfall = WeatherExtremeValue(
                        value=weather_record.snowfall,
                        record_time=weather_record.record_time,
                        duty_id=duty_record.id if hasattr(duty_record, 'id') else None
                    )
                
                # 更新最大风速
                if max_wind_speed is None or weather_record.wind_speed > max_wind_speed.value:
                    max_wind_speed = WeatherExtremeValue(
                        value=weather_record.wind_speed,
                        record_time=weather_record.record_time,
                        duty_id=duty_record.id if hasattr(duty_record, 'id') else None
                    )
        
        # 如果没有找到任何天气记录，设置默认值
        if max_temperature is None:
            max_temperature = WeatherExtremeValue(value=0, record_time=None)
        if min_temperature is None:
            min_temperature = WeatherExtremeValue(value=0, record_time=None)
        if max_rainfall is None:
            max_rainfall = WeatherExtremeValue(value=0, record_time=None)
        if max_snowfall is None:
            max_snowfall = WeatherExtremeValue(value=0, record_time=None)
        if max_wind_speed is None:
            max_wind_speed = WeatherExtremeValue(value=0, record_time=None)
        
        # 构建并返回响应对象
        return WeatherExtremeStats(
            personnel_certificate_number=personnel_certificate_number,
            personnel_name=personnel.name,
            year=year,
            max_temperature=max_temperature,
            min_temperature=min_temperature,
            max_rainfall=max_rainfall,
            max_snowfall=max_snowfall,
            max_wind_speed=max_wind_speed,
            total_duty_days=total_duty_days,
            total_duty_hours=total_duty_hours
        )
    
    @staticmethod
    def get_extreme_weather_duty_stat(db: Session, personnel_certificate_number: str, year: str) -> ExtremeWeatherDutyStat:
        """
        统计指定人员在特定年份的极端天气值班记录
        
        Args:
            db: 数据库会话
            personnel_certificate_number: 人员证件号
            year: 年份（YYYY格式）
            
        Returns:
            ExtremeWeatherDutyStat: 极端天气值班统计结果
        """
        # 验证年份格式
        try:
            year_int = int(year)
        except ValueError:
            raise ValueError("年份格式错误，请使用YYYY格式")
        
        # 查询人员信息
        personnel = db.query(Personnel).filter(
            Personnel.certificate_number == personnel_certificate_number
        ).first()
        
        if not personnel:
            raise ValueError(f"未找到证件号为 {personnel_certificate_number} 的人员")
        
        # 查询该人员该年的所有值班记录
        duty_records = db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            extract('year', DutyRecord.start_time) == year_int
        ).all()
        
        # 极端天气类型定义
        extreme_weather_types = ["炎热", "酷热", "严寒", "极寒", "大雨", "暴雨", "暴雪", "大雪", "大风", "烈风"]
        
        # 初始化数据收集变量
        extreme_duty_records = []
        weather_type_count: Dict[str, int] = {}
        total_duty_days = 0
        total_duty_hours = 0.0
        unique_duty_dates = set()
        
        # 遍历每条值班记录
        for record in duty_records:
            # 计算值班时长和天数
            start_time = record.start_time
            end_time = record.end_time
            
            # 计算值班时长（小时）
            duration_hours = (end_time - start_time).total_seconds() / 3600
            total_duty_hours += duration_hours
            
            # 记录唯一的值班日期
            current_date = start_time.date()
            unique_duty_dates.add(current_date)
            
            # 计算中位数时间（值班记录的中点时间）
            median_time = start_time + (end_time - start_time) / 2
            
            # 找到中位数时间所在小时的整点时间（用于匹配天气记录）
            median_hour = median_time.replace(minute=0, second=0, microsecond=0)
            
            # 使用SQLite兼容的方式查询小时匹配的天气记录
            hour_start = median_hour
            hour_end = median_hour + timedelta(hours=1)
            
            # 通过关联关系获取工位，再获取部门编码
            dept_code = None
            if record.workstation:
                dept_code = record.workstation.dept_code

            # 使用部门编码查询天气记录
            weather_record = db.query(WeatherRecord).filter(
                WeatherRecord.dept_code == dept_code,
                WeatherRecord.record_time >= hour_start,
                WeatherRecord.record_time < hour_end
            ).first()
            
            # 如果找到天气记录，检查是否包含极端天气
            has_extreme_weather = False
            if weather_record:
                try:
                    # 获取天气状况列表
                    weather_conditions = weather_record.weather_conditions_array
                    
                    # 统计每种天气状况的出现次数
                    for condition in weather_conditions:
                        if condition in weather_type_count:
                            weather_type_count[condition] += 1
                        else:
                            weather_type_count[condition] = 1
                    
                    # 判断是否包含极端天气
                    if any(condition in extreme_weather_types for condition in weather_conditions):
                        has_extreme_weather = True
                except Exception as e:
                    # 如果解析出错，跳过这条记录
                    continue
            
            # 如果是极端天气，添加到极端值班记录列表
            if has_extreme_weather:
                extreme_duty_records.append(
                    ExtremeWeatherDutyRecord(
                        duty_id=str(record.id),
                        duty_date=start_time
                    )
                )
        
        # 计算总值班天数
        total_duty_days = len(unique_duty_dates)
        
        # 构建天气类型汇总
        weather_type_summary = [
            WeatherTypeSummary(type=weather_type, count=count)
            for weather_type, count in weather_type_count.items()
            if weather_type in extreme_weather_types
        ]
        
        # 构建返回结果
        return ExtremeWeatherDutyStat(
            personnel_id=personnel_certificate_number,
            personnel_name=personnel.name,
            year=year,
            total_duty_days=total_duty_days,
            total_duty_hours=round(total_duty_hours, 2),
            total_duty_records=len(duty_records),
            extreme_duty_records=extreme_duty_records,
            weather_type_summary=weather_type_summary
        )
