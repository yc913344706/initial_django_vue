import datetime
from decimal import Decimal
import pytz
from schema import Schema, And, Use, Or
import json
import re
from pydantic import validate_call
from django.db import connection


def pub_phone_check_service(value, error_msg=None):
    """
    手机/电话号码规则校验(手机号纯数字，电话号码支持区分010-12345678)
    :param value:
    :param error_msg:
    :return:
    """
    if not value:
        return None
    mail_phone_p = re.compile('^((1[0-9]{10})|(((([0-9]{3,4}-)?[0-9]{8})|(([0-9]{4}-)?[0-9]{7}))(-[0-9]{1,4})?))$')
    if not mail_phone_p.search(value):
        if error_msg:
            raise ValueError(error_msg)
        raise ValueError(f'异常的手机/电话号码:{value}')
    return value


def pub_hans_check_service(value, is_must=False, error_msg=None):
    """
    汉字检查
    :param value:
    :param error_msg:
    :return:
    """
    if not value:
        if is_must:
            if error_msg:
                raise ValueError(error_msg)
            else:
                raise ValueError('缺少必须的汉字内容！')
        return None
    # p = re.compile('[^\x00-\xff]|[a-zA-Z0-9]|[^0-9A-Za-z\u4e00-\u9fa5ぁ-んァ-ヶ\uAC00-\uD7A3]')  # admin后台有自己的验证
    # res = p.findall(value)
    res = re.findall('[\u4e00-\u9fa5]', value)
    if not res:
        if is_must:
            if error_msg:
                raise ValueError(error_msg)
            else:
                raise ValueError('缺少必须的汉字内容！')
    return value


def pub_request_bool_check(bool_msg):
    if type(bool_msg) == bool:
        return bool_msg
    if not bool_msg:
        return False
    if str(bool_msg) in ['True', 'true']:
        return True
    return False


def pub_json_list_check(file_list, error_msg=None):
    if not file_list:
        return []
    if type(file_list) == list:
        return file_list
    try:
        file_list = json.loads(file_list)
    except Exception as e:
        if not error_msg:
            raise ValueError('数据异常：仅接受数组字段!')
        else:
            raise ValueError(error_msg)
    if type(file_list) != list:
        if not error_msg:
            raise ValueError('数据异常：仅接受数组字段!')
        else:
            raise ValueError(error_msg)
    return file_list


def pub_flot_check(status, error_msg=None):
    """flot类型检查"""
    if status in [0, '0']:
        return 0
    if not status:
        return None
    if status:
        try:
            status = Decimal(str(status))
            if status > 9999999999:
                raise ValueError('参数值过大!')
            return status
        except:
            if error_msg:
                raise ValueError(error_msg)
            else:
                raise ValueError('参数类型异常，不支持非数字类型!')
    return 0


def pub_int_check(status, error_msg=None):
    """int类型检查"""
    error_msg = '参数类型异常，不支持非int类型!' if not error_msg else error_msg
    status_check = Schema(Use(int), error=error_msg)
    return status_check.validate(status)

def pub_check_date_with_format(date_str: str, format_str: str, to_utc: bool = False):
    """
    将日期字符串转换为 datetime 对象，并支持转换为 UTC 时间
    
    :param date_str: 日期字符串
    :param format_str: 日期格式字符串，例如：'%Y-%m-%d %H:%M:%S'
    :param to_utc: 是否转换为 UTC 时间，默认为 False
    :return: 转换后的 datetime 对象，如果解析失败则返回 None
    """
    try:
        # 解析时间字符串
        parsed_datetime = datetime.datetime.strptime(date_str, format_str)

        if to_utc:
            # 如果没有时区信息，则假设为本地时间并转换为 UTC
            if parsed_datetime.tzinfo is None:
                parsed_datetime = pytz.timezone('UTC').localize(parsed_datetime)
            else:
                parsed_datetime = parsed_datetime.astimezone(pytz.utc)

        return parsed_datetime
    except ValueError:
        return None

def pub_check_date_tool(date, error_msg=None):
    """日期参数校验"""
    if not date or date == 'null':
        return None
    try:
        if type(date) == str:
            date = date.replace('T00:00:00','')
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date
    except Exception as e:
        if not error_msg:
            raise ValueError(f'日期参数异常:{e}')
        else:
            raise ValueError(f'{error_msg}:{e}')

def pub_check_date_yunhao_tool(date, error_msg=None):
    """日期参数校验"""
    if not date or date == 'null':
        return None
    try:
        if type(date) == str:
            date = date.replace('T00:00:00','')
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date
    except Exception as e:
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
            return date.date
        except Exception as e:
            if not error_msg:
                raise ValueError(f'日期参数异常:{e}')
            else:
                raise ValueError(f'{error_msg}:{e}')


def pub_check_id_status_tool(status, check_list: list, error_msg=None, is_none=True):
    """id参数校验"""
    error_msg = error_msg if error_msg else 'status参数异常!'
    if is_none:
        status_check = Schema(Or(None, '', And(Use(int), lambda i: i in check_list)), error=error_msg)
    else:
        status_check = Schema(And(Use(int), lambda i: i in check_list), error=error_msg)
    return status_check.validate(status)


def pub_check_page_num_tool(page_num, is_max=False):
    try:
        page_num = int(page_num)
        if page_num < 0:
            return 20
        if is_max and page_num > 100:
            return 100
        return page_num
    except:
        return 20


def pub_check_pid_tool(pid):
    try:
        pid = int(pid)
        if pid < 1:
            return 1
        return pid
    except:
        return 1

def my_custom_sql(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchone()

    return results[0]


def pub_date_check(date, error_msg=None):
    if not date:
        return None
    try:
        this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except Exception as e:
        if not error_msg:
            raise ValueError(f'日期参数异常:{e}')
        else:
            raise ValueError(error_msg)
    return date


def pub_month_date_check(date, error_msg=None):
    if not date:
        return None
    try:
        this_date = datetime.datetime.strptime(date, '%Y-%m').date()
        return this_date
    except Exception as e:
        if not error_msg:
            raise ValueError(f'日期参数异常:{e}')
        else:
            raise ValueError(error_msg)


def pub_check_value_length(value, length, error_msg=None):
    if not value:
        return None
    if type(value) != str:
        value = str(value)
    if len(value) > length:
        if not error_msg:
            raise ValueError(f'字符串超过最大长度限制:{length}')
        else:
            raise ValueError(error_msg)
    return value


def pub_check_must_value(value, length=2, error_msg=None):
    try:
        if not value:
            raise ValueError('缺少必填参数!')
        value2 = value.replace(' ', '').replace('\n', '')
        if not value2 or len(value2) < length:
            raise ValueError('缺少必填参数或参数长度不足!')
        return value
    except Exception as e:
        if not error_msg:
            raise e
        else:
            raise ValueError(error_msg)


@validate_call()
def pub_check_positive_integer(n: int, max_num: int = 0, value_name: str = '', error_msg: str = '', ):
    """
    判断一个数是否未正整数
    :param n:
    :param max_num: 最大值判断
    :param value_name: 参数名
    :param error_msg: 自定义报错原因
    :return:
    """
    if isinstance(n, int) and n > 0:
        if max_num and n > max_num:
            raise ValueError(f'{value_name}异常:支持的最大值为:{max_num}')
        return n
    else:
        if error_msg:
            raise ValueError(error_msg)
        else:
            if value_name:
                raise ValueError(f"{value_name}的值必须为正整数!")
            else:
                raise ValueError(f'参数值必须为正整数,当前值:{n}')


def pub_new_flot_bool_check(n: str):
    """
    检查一个参数是否为浮点
    :param n:
    :return:
    """
    if not n:
        return False
    n = str(n)
    float_regex = r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'
    return re.match(float_regex, n) is not None


def pub_convert_number(num: int, need_length: int):
    """
    用0填充补齐数字字符至指定长度
    :param num:
    :param need_length:
    :return:
    """
    if not num:
        num = 1
    num_str = str(num)  # 将数字转换为字符串
    num_str_padded = num_str.zfill(need_length)  # 使用 zfill 函数在字符串前面填充0，使其总长度为4
    return num_str_padded
