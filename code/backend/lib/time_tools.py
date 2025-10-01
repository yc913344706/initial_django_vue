import json
import math
import time
from uuid import UUID
from datetime import datetime, timedelta, timezone as dt_timezone
from dateutil.relativedelta import relativedelta
import pytz
import http.client
import urllib
from lib.log import color_logger
from django.utils import timezone as django_timezone
from collections import OrderedDict
from backend.settings import config_data

from lib.redis_tool import get_redis_value, set_redis_value

def get_now_time_utc_obj():
    """获取当前时间UTC对象"""
    return datetime.now(dt_timezone.utc)

def utc_obj_to_time_zone_str(utc_time_obj: datetime, format_str: str = '%Y-%m-%d %H:%M:%S', time_zone: str = 'Asia/Shanghai'):
    if utc_time_obj is None:
        return None
    timezone_obj = utc_obj_to_timezone_obj(utc_time_obj, time_zone)
    return timezone_obj.strftime(format_str)


def utc_obj_to_timezone_obj(utc_time_obj: datetime, time_zone: str = 'Asia/Shanghai'):
    """
    将 UTC 时间转换为指定时区的 datetime 对象。
    
    参数:
    - utc_time_obj (datetime): UTC 时间的 datetime 对象
    - time_zone (str): 目标时区，例如 'Asia/Shanghai'
    """
    shanghai_tz = pytz.timezone(time_zone)
    
    # 确保时间是带时区的，如果不带时区则假定为 UTC
    if django_timezone.is_naive(utc_time_obj):
        utc_time_obj = pytz.utc.localize(utc_time_obj)
    
    # 转换到上海时区
    time_zone_obj = utc_time_obj.astimezone(shanghai_tz)

    return time_zone_obj


def timezone_obj_to_utc_obj(timezone_obj: datetime):
    """
    将带时区的时间转换为 UTC 时间
    
    参数:
    - timezone_obj (datetime): 带时区的 datetime 对象
    """
    # 将带时区的时间转换为 UTC 时间
    return timezone_obj.astimezone(pytz.utc)


def get_utc_obj_from_str(date_str, date_format_str):
    """
    将输入的日期字符串转换为 UTC 时间的 datetime 对象。
    
    参数:
    - date_str (str): 输入的日期字符串，例如 '2025-01-07'
    - date_format_str (str): 日期格式字符串，例如 '%Y-%m-%d'
    
    返回:
    - datetime: 转换后的 UTC datetime 对象
    """
    # 将输入日期字符串解析为本地时间的 naive datetime 对象
    naive_datetime = datetime.strptime(date_str, date_format_str)
    # 为 naive datetime 设置 UTC 时区
    utc_datetime = naive_datetime.replace(tzinfo=dt_timezone.utc)
    return utc_datetime


def get_timezone_obj_from_str(datetime_str, date_format_str='%Y-%m-%d %H:%M:%S', time_zone: str = 'Asia/Shanghai'):
    """
    将无时区的时间字符串转换为指定时区的 datetime 对象。
    
    参数:
    - datetime_str (str): 无时区的时间字符串，例如 '2025-01-07 10:00:00'
    - date_format_str (str): 日期格式字符串，例如 '%Y-%m-%d %H:%M:%S'
    """
    # 将字符串解析为 datetime 对象（无时区）
    naive_datetime = datetime.strptime(datetime_str, date_format_str)
    # 定义东八区时区
    tz = pytz.timezone(time_zone)
    # 为 naive 的 datetime 添加东八区时区信息
    return tz.localize(naive_datetime)


def get_delta_seconds_from_now_to_utc_obj(utc_time_obj: datetime):
    now_utc_obj = get_now_time_utc_obj()
    
    if now_utc_obj > utc_time_obj:
        delta_seconds = (now_utc_obj - utc_time_obj).total_seconds()
    else:
        delta_seconds = (utc_time_obj - now_utc_obj).total_seconds()

    return delta_seconds


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return utc_obj_to_time_zone_str(o)
            # return o.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

        if isinstance(o, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return o.hex
        # return json.JSONEncoder.default(self, o)

        return super(CustomEncoder, self).default(o)


def get_previous_months(skip_days: int = 0, need_last_year: bool = False) -> list:
    today = datetime.today()
    months = []

    if need_last_year:
        # 计算并包括去年同期到当前月的前一个月
        for i in range(1, 13):
            target_date = today - relativedelta(months=i + (1 if today.day <= skip_days else 0))
            months.append(target_date.strftime('%Y-%m'))
        months.reverse()
    else:
        # 检查今天的日期是否小于或等于skip_days，如果是，则考虑上个月
        target_month = today - relativedelta(months=(2 if today.day <= skip_days else 1))
        months.append(target_month.strftime('%Y-%m'))

    return months


def get_milliseconds_timestamp():
    return int(time.time() * 1000)

def get_year_month_holidays(year, month):
    """获取指定年份和月份的节假日信息"""
    if not year or not month:
        color_logger.error("年份或月份不能为空")
        return []
    
    redis_key_name = f"holidays_{year}_{month}"
    redis_key_value = get_redis_value(
        redis_db_name='DEFAULT',
        redis_key_name=redis_key_name
    )

    if redis_key_value:
        return redis_key_value

    month_holidays = get_realtime_year_month_holidays(year, month)
    if month_holidays:
        set_redis_value(
            redis_db_name='DEFAULT',
            redis_key_name=redis_key_name,
            redis_key_value=month_holidays,
            set_expire=None
        )
    
    return month_holidays

def is_workday(date):
    """判断是否为工作日"""
    year_month_holidays = get_year_month_holidays(date.year, date.month)

    date_str = date.strftime('%Y-%m-%d')
    assert date_str in year_month_holidays, f"未找到 {date_str} 的节假日信息"
    """
    daycode表示日期类型，0表示工作日、1节假日、2双休日、3调休日（需上班）。
    判断是否需要上班建议用isnotwork字段，其中值为0表示上班，为1表示休息。
    wage表示薪资倍数，周末为两倍，法定节假日当天为三倍其他两倍（按年查询时返回三倍薪资的具体日期）。
    """
    return year_month_holidays[date_str]['isnotwork'] == 0

def get_workday_delta(start_time: datetime, end_time: datetime) -> int:
    """
    计算两个时间点之间的工作日数
    只计算工作日，不包括节假日
    """
    if not start_time or not end_time or start_time > end_time:
        return 0
        
    # 初始化工作日计数
    workdays = 0
    current_date = start_time.date()
    end_date = end_time.date()
    
    # 如果是同一天，直接判断是否为工作日
    if current_date == end_date:
        return 1 if is_workday(current_date) else 0
    
    # 遍历日期范围
    while current_date <= end_date:
        try:
            # 判断是否为工作日
            if is_workday(current_date):
                workdays += 1
        except Exception as e:
            color_logger.error(f"计算工作日时出错 {current_date}: {str(e)}")
            # 如果获取节假日信息失败，按照默认规则处理（周一到周五为工作日）
            if current_date.weekday() < 5:  # 0-4 表示周一到周五
                workdays += 1
        
        # 移动到下一天
        current_date += timedelta(days=1)
    
    return workdays


def format_minutes_to_human_readable(minutes: int) -> str:
    """
    将分钟数转换为人类可读的格式
    例如：
    - 100分钟转换为1小时40分钟
    - 1000分钟转换为16小时40分钟
    - 10000分钟转换为6天22小时40分钟
    """
    if not minutes or minutes < 0:
        return "时间不能为负数"
    
    # 处理浮点数
    total_minutes = round(float(minutes))
    
    days = minutes // (24 * 60)
    hours = (minutes % (24 * 60)) // 60
    remaining_minutes = round(minutes % 60)

    # 构建结果字符串
    result = []
    if days > 0:
        result.append(f"{days}天")
    if hours > 0:
        result.append(f"{hours}小时")
    if remaining_minutes > 0:  # 只有当有剩余分钟时才显示
        result.append(f"{remaining_minutes}分钟")
    elif not result:  # 如果没有天和小时，且分钟为0，则显示"0分钟"
        return "0分钟"

    return "".join(result)

def split_date(start_date: datetime, end_date: datetime):
    """
    将日期范围拆分为多个区间
    支持按天、周、月、季度、年拆分
    返回格式：
    {
        '2025-01-01': [datetime('2025-01-01'), datetime('2025-01-02')],
        '2025-01-02': [datetime('2025-01-02'), datetime('2025-01-03')],
        ...
    }
    """
    color_logger.debug(f"start split_date")

    def get_week_range(date):
        """根据日期计算当前周的起止日期（以周一为起点）"""
        start_of_week = date - timedelta(days=date.weekday())  # 本周周一
        end_of_week = start_of_week + timedelta(days=6)  # 本周周日
        return start_of_week, end_of_week

    def get_month_range(year, month):
        """给定年和月，返回该月的起止日期"""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
        return utc_obj_to_timezone_obj(start), utc_obj_to_timezone_obj(end)

    assert isinstance(start_date, datetime) and isinstance(end_date, datetime), "开始日期和结束日期必须是 datetime 对象"

    # 将输入的日期字符串转为 datetime 对象
    # start_date = datetime.strptime(start_date, "%Y-%m-%d")
    # end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 检查输入是否合法
    if end_date < start_date:
        raise ValueError("结束日期不能早于开始日期")
    
    # 计算天数跨度
    total_days = (end_date - start_date).days + 1

    # 用来存储结果
    result = OrderedDict()
    
    if total_days <= 9:
        color_logger.debug(f"total_days <= 9")
        # 如果总天数不超过 9 天，按天拆分
        current = start_date
        while current < end_date:
            key = current.strftime('%Y-%m-%d')
            result[key] = [current, current+timedelta(days=1)]
            current += timedelta(days=1)
    elif total_days <= 45:
        color_logger.debug(f"total_days <= 45")
        # 如果总天数 > 9 天 且 ≤ 45 天，按周拆分
        current = start_date
        while current <= end_date:
            week_start, week_end = get_week_range(current)
            range_start = max(start_date, week_start)
            range_end = min(end_date, week_end)
            key = f"{range_start.strftime('%Y')}W{range_start.strftime('%W')}"  # 按年第几周标记
            result[key] = [range_start, range_end+timedelta(days=1)]
            current = range_end + timedelta(days=1)
    elif total_days < 270:
        color_logger.debug(f"total_days < 270")
        # 如果总天数 > 45 天 且 < 9 个月，按月拆分
        current = start_date
        while current <= end_date:
            month_start, month_end = get_month_range(current.year, current.month)
            range_start = max(start_date, month_start)
            range_end = min(end_date, month_end)
            key = f"{range_start.strftime('%Y')}M{range_start.strftime('%m')}"
            result[key] = [range_start, range_end+timedelta(days=1)]
            current = range_end + timedelta(days=1)
    elif total_days < 547:
        color_logger.debug(f"total_days < 547")
        # 如果总天数 ≥ 9 个月 且 < 1 年半，按季度拆分
        current = start_date
        while current <= end_date:
            year = current.year
            quarter = math.ceil(current.month / 3)  # 第几季度
            quarter_start = datetime(year, (quarter - 1) * 3 + 1, 1)
            if quarter == 4:
                quarter_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                quarter_end = datetime(year, quarter * 3 + 1, 1) - timedelta(days=1)
            quarter_start = utc_obj_to_timezone_obj(quarter_start)
            quarter_end = utc_obj_to_timezone_obj(quarter_end)
            range_start = max(start_date, quarter_start)
            range_end = min(end_date, quarter_end)
            key = f"{year}Q{quarter}"
            result[key] = [range_start, range_end+timedelta(days=1)]
            current = range_end + timedelta(days=1)
    else:
        color_logger.debug(f"total_days >= 547")
        # 如果总天数 ≥ 1 年半，按年拆分
        current = start_date
        while current <= end_date:
            year_start = datetime(current.year, 1, 1)
            year_end = datetime(current.year + 1, 1, 1) - timedelta(days=1)
            year_start = utc_obj_to_timezone_obj(year_start)
            year_end = utc_obj_to_timezone_obj(year_end)
            range_start = max(start_date, year_start)
            range_end = min(end_date, year_end)
            key = range_start.strftime("%Y")
            result[key] = [range_start, range_end+timedelta(days=1)]
            current = range_end + timedelta(days=1)

    return result


# 和config_data相关
from backend.settings import config_data

def get_realtime_year_month_holidays(year, month):
    """
    获取指定年份和月份的中国节假日信息（动态获取）
    
    参数:
        year (int): 查询的年份
        month (int): 查询的月份
    返回:
        dict: 包含所有节假日信息的字典，按月整合
    """
    if not year or not month:
        color_logger.error("年份或月份不能为空")
        return []
    
    month_holidays = []
    api_key = config_data.get('TIANXING_API_KEY')
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    # 格式化参数
    date_param = f"{year}-{month:02d}"  # 年-月，确保月份是两位数
    params = urllib.parse.urlencode({'key': api_key, 'type': 2, 'date': date_param})
    
    try:
        # 发起请求
        conn.request('POST', '/jiejiari/index', params, headers)
        response = conn.getresponse()
        result = response.read().decode('utf-8')  # 响应数据
        
        # 解析 JSON 数据
        dict_data = json.loads(result)
        # https://www.tianapi.com/apiview/139-1
        """
        {
            "code": 200,
            "msg": "success",
            "result": {
                "list": [
                {
                    "date": "2021-01-01",
                    "daycode": 1,
                    "weekday": 5,
                    "cnweekday": "星期五",
                    "lunaryear": "庚子",
                    "lunarmonth": "冬月",
                    "lunarday": "十八",
                    "info": "节假日",
                    "start": 0,
                    "now": 0,
                    "end": 2,
                    "holiday": "1月1号",
                    "name": "元旦节",
                    "enname": "New Year's Day",
                    "isnotwork": 1,
                    "vacation": [
                    "2021-01-01",
                    "2021-01-02",
                    "2021-01-03"
                    ],
                    "remark": "",
                    "wage": 3,
                    "tip": "1月1日放假，共3天。",
                    "rest": "2020年12月28日至12月31日请假4天，与周末连休可拼七天长假。"
                }
                ]
            }
            }
        """
        
        # 检查返回状态
        if dict_data.get('code') == 200 and 'result' in dict_data:
            # 合并当前月份的节假日信息
            month_holidays = dict_data['result'].get('list', [])

            # 将节假日信息按日期排序
            month_holidays = {item['date']: item for item in month_holidays}

            color_logger.info(f"获取{date_param}的节假日成功")
            return month_holidays
        else:
            color_logger.warning(f"获取{date_param}的节假日失败")
    
    except Exception as e:
        color_logger.error(f"获取{date_param}的节假日失败: {e}")

    conn.close()
    return month_holidays

def current_is_worktime():
    """判断当前是否处于工作时间"""

    now = django_timezone.now().astimezone(pytz.timezone('Asia/Shanghai'))
    
    # 解析工作时间配置
    workday_start = datetime.strptime(
        '09:00',
        '%H:%M'
    ).time()
    workday_end = datetime.strptime(
        '19:00',
        '%H:%M'
    ).time()

    current_time = now.time()
    is_work_result = is_workday(now) and \
        current_time >= workday_start and \
        current_time <= workday_end
    
    return is_work_result

def calculate_working_minutes(start_time: datetime, end_time: datetime) -> int:
    """
    计算两个时间点之间的工作时间（分钟）
    工作时间定义为工作日的 WORKDAY_START_TIME - WORKDAY_END_TIME
    """
    if not start_time or not end_time or start_time > end_time:
        return 0
        
    # 转换时间到上海时区
    start_time = utc_obj_to_timezone_obj(start_time)
    end_time = utc_obj_to_timezone_obj(end_time)
    
    color_logger.debug(f"计算工单 working_minutes. start_time: {start_time}, end_time: {end_time}")

    # 获取工作时间配置
    workday_start_time = datetime.strptime(
        '09:00',
        '%H:%M'
    ).time()
    workday_end_time = datetime.strptime(
        '19:00',
        '%H:%M'
    ).time()

    # 初始化总工作分钟数
    total_minutes = 0
    
    # 获取日期部分
    current_date = start_time.date()
    end_date = end_time.date()

    # 如果是同一天
    if current_date == end_date:
        color_logger.debug(f"计算工单 working_minutes: 同一天")
        if is_workday(current_date):
            # 获取当天的工作时间范围（不带时区）
            day_start = datetime.combine(current_date, workday_start_time)
            day_end = datetime.combine(current_date, workday_end_time)
            
            # 转换为上海时区
            day_start = day_start.replace(tzinfo=start_time.tzinfo)
            day_end = day_end.replace(tzinfo=start_time.tzinfo)
            
            color_logger.debug(f"工作时间范围 - 开始: {day_start}, 结束: {day_end}")
            
            # 调整计算区间
            calc_start = max(start_time, day_start)
            calc_end = min(end_time, day_end)
            
            color_logger.debug(f"实际计算区间 - 开始: {calc_start}, 结束: {calc_end}")
            
            if calc_start < calc_end:
                minutes = int((calc_end - calc_start).total_seconds() / 60)
                total_minutes += minutes
                color_logger.debug(f"计算得到工作时间: {minutes} 分钟")
            
        return total_minutes

    # 如果跨天，分三段计算
    # 1. 第一天的工作时间
    if is_workday(current_date):
        day_start = datetime.combine(current_date, workday_start_time)
        day_end = datetime.combine(current_date, workday_end_time)
        
        day_start = day_start.replace(tzinfo=start_time.tzinfo)
        day_end = day_end.replace(tzinfo=start_time.tzinfo)
        
        calc_start = max(start_time, day_start)
        if calc_start < day_end:
            total_minutes += int((day_end - calc_start).total_seconds() / 60)

    # 2. 中间天的工作时间
    current_date += timedelta(days=1)
    while current_date < end_date:
        if is_workday(current_date):
            day_start = datetime.combine(current_date, workday_start_time)
            day_end = datetime.combine(current_date, workday_end_time)
            
            day_start = day_start.replace(tzinfo=start_time.tzinfo)
            day_end = day_end.replace(tzinfo=start_time.tzinfo)
            
            total_minutes += int((day_end - day_start).total_seconds() / 60)
        current_date += timedelta(days=1)

    # 3. 最后一天的工作时间
    if is_workday(end_date):
        day_start = datetime.combine(end_date, workday_start_time)
        day_end = datetime.combine(end_date, workday_end_time)
        
        day_start = day_start.replace(tzinfo=start_time.tzinfo)
        day_end = day_end.replace(tzinfo=start_time.tzinfo)
        
        calc_end = min(end_time, day_end)
        if day_start < calc_end:
            total_minutes += int((calc_end - day_start).total_seconds() / 60)

    return total_minutes

