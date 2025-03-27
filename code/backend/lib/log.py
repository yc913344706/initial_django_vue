import logging
import logging.handlers
import os
import sys

# 定义一个标志变量，用于标记是否已经设置过日志级别
_level_set = False

class ColorHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a stream. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.
    """

    terminator = '\n'
    bule = 96 if os.name == 'nt' else 36
    yellow = 93 if os.name == 'nt' else 33

    def __init__(self, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        logging.Handler.__init__(self)
        if stream is None:
            stream = sys.stdout  # stderr无彩。
        self.stream = stream

    def flush(self):
        """
        Flushes the stream.
        """
        self.acquire()
        try:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
        finally:
            self.release()

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        # noinspection PyBroadException
        try:
            msg = self.format(record)
            stream = self.stream
            if record.levelno == 10:
                msg_color = ('\033[0;32m%s\033[0m' % msg)  # 绿色
            elif record.levelno == 20:
                msg_color = ('\033[0;%sm%s\033[0m' % (self.bule, msg))  # 青蓝色 36    96
            elif record.levelno == 30:
                msg_color = ('\033[0;%sm%s\033[0m' % (self.yellow, msg))
            elif record.levelno == 40:
                msg_color = ('\033[0;35m%s\033[0m' % msg)  # 紫红色
            elif record.levelno == 50:
                msg_color = ('\033[0;31m%s\033[0m' % msg)  # 血红色
            else:
                msg_color = msg
            stream.write(msg_color)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = getattr(self.stream, 'name', '')
        if name:
            name += ' '
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)


formatter_dict = {
    1: logging.Formatter(
        '日志时间【%(asctime)s.%(msecs)03d】 - 日志名称【%(name)s】 - 文件【%(filename)s】 - 第【%(lineno)d】行 - 日志等级【%(levelname)s】 - 日志信息【%(message)s】',
        "%Y-%m-%d %H:%M:%S"),
    2: logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s',
        "%Y-%m-%d %H:%M:%S"),
    3: logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - 【 File "%(pathname)s", line %(lineno)d, in %(funcName)s 】 - %(levelname)s - %(message)s',
        "%Y-%m-%d %H:%M:%S"),  # 一个模仿traceback异常的可跳转到打印日志地方的模板
    4: logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - "%(filename)s" - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s -               File "%(pathname)s", line %(lineno)d ',
        "%Y-%m-%d %H:%M:%S"),  # 这个也支持日志跳转
    5: logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - "%(pathname)s:%(lineno)d" - %(funcName)s - %(levelname)s - %(message)s',
        "%Y-%m-%d %H:%M:%S"),  # 我认为的最好的模板,推荐
    6: logging.Formatter('%(name)s - %(asctime)-15s.%(msecs)03d - %(filename)s - %(lineno)d - %(levelname)s: %(message)s',
                         "%Y-%m-%d %H:%M:%S"),
    7: logging.Formatter('%(levelname)s - %(filename)s - %(lineno)d - %(message)s'),  # 一个只显示简短文件名和所处行数的日志模板
}


def get_color_console_logger(formatter_template=5):
    # 下面这行注释不要删除，使用这个彩色输出控制的前置操作。
    # pycharm --> preferences--> console colors --> console --> error output -->foreground 勾去掉
    logger = logging.getLogger("控制台彩色输出")
        # 检查是否已经设置过日志级别

    global _level_set  # 使用全局变量来记录日志级别是否已设置
    if not _level_set:
        logger.setLevel(logging.DEBUG)
        _level_set = True  # 标记日志级别已经设置

    stream_handler = ColorHandler()  # 不使用streamhandler，使用自定义的彩色日志
    stream_handler.setFormatter(formatter_dict[formatter_template])
    logger.addHandler(stream_handler)
    return logger


# common_logger = get_file_logger()

color_logger = get_color_console_logger()

def set_color_logger_level(level):
    color_logger.setLevel(level)
