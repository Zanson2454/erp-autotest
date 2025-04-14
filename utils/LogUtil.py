from loguru import logger
import time
import os,sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
    
from config.config import Config

log_path = Config.get_log_dir()  # 获取日志路径
t = time.strftime("%Y_%m_%d")  # 获取当前时间作为文件名
log_extension = ".log"  # 默认日志文件扩展名
log_level = "INFO"  # 默认日志等级
logfile = os.path.join(log_path, "log_{}".format(t) + log_extension)  # 拼接日志文件

# 封装log工具类
class Loggers:
    # 添加日志到标准工作流
    logger.add(sys.stderr,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|{module}.{function} line:{line}|<level>{message}</level>",
               filter='my module',
               level='DEBUG')
    # 日志写入文件
    logger.add(logfile,
               format="<yellow>{time:YYYY-MM-DD HH:mm:ss}</yellow>|{module}.{function} line:{line}| <level>{message}</level>",
               level=log_level,
               rotation="00:00", retention='7 days',
               encoding="utf-8", enqueue=True)

    def info(self, msg,**kwargs):
        return logger.info(msg,**kwargs)

    def debug(self, msg,**kwargs):
        return logger.debug(msg,**kwargs)

    def warning(self, msg,**kwargs):
        return logger.warning(msg,**kwargs)

    def error(self, msg,**kwargs):
        return logger.error(msg,**kwargs)

    def critical(self,msg,**kwargs):
        return logger.critical(msg,**kwargs)


if __name__ == '__main__':
    loggers = Loggers()
    loggers.debug("调试消息")
    loggers.info("普通消息")
    loggers.warning("警告消息")
    loggers.error("错误消息")
    loggers.critical("严重错误消息")

