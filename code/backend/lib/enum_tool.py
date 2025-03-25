from enum import IntEnum

from lib.parameter_check_tool import pub_check_id_status_tool

class BaseEnum(IntEnum):

    @classmethod
    def return_tuple(cls):
        return ()

    @classmethod
    def get_str(cls, value_id):
        for i in cls.return_tuple():
            if i[0] == value_id:
                return i[1]
        return ''

    @classmethod
    def get_value_id(cls, value_name):
        for i in cls.return_tuple():
            if i[1] == value_name:
                return i[0]
        return None

    @classmethod
    def return_json_dict(cls):
        pass

    @classmethod
    def check_value(cls, value_id, error_msg, is_null=True):
        return pub_check_id_status_tool(value_id, [i.value for i in cls], error_msg, is_null)
