import logging
import inspect
from logging.handlers import RotatingFileHandler
import sys
import os

__all__ = ["getLogger"]


def _override():
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    SUCCESS = 25
    TASK = 23
    INFO = 20
    DEBUG = 10
    TRACE = 5
    NOTSET = 0

    attr = locals().copy()
    for l_name, l_val in attr.items():
        setattr(logging, l_name, l_val)

    logging.addLevelName(SUCCESS, "SUCCESS")
    logging.addLevelName(TRACE, "TRACE")
    logging.addLevelName(TASK, "TASK")

    def _fill_log(self):
        res = inspect.stack()[3][0]
        func_name = res.f_code.co_filename.replace('/', '\\').split('\\')[-1]
        mod_name = res.f_code.co_name
        PREF = "-----"
        GID = "-----"
        if 'PREF' in res.f_globals:
            PREF = res.f_globals['PREF']
        if 'GID' in res.f_globals:
            GID = res.f_globals['GID']
        if 'PREF' in res.f_locals:
            PREF = res.f_locals['PREF']
        if 'GID' in res.f_locals:
            GID = res.f_locals['GID']
        if "self" in res.f_locals:
            self_obj = res.f_locals["self"]
            if hasattr(self_obj, 'PREF'):
                PREF = self_obj.PREF
            if hasattr(self_obj, 'GID'):
                GID = self_obj.GID
        ext = {'prefix': PREF, 'globalid': GID, 'modulename': mod_name, 'funcname': func_name}
        return ext

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, extra=self._fill_log(), **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, extra=self._fill_log(), **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, extra=self._fill_log(), **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            if 'extra' not in kwargs:
                kwargs['extra'] = self._fill_log()
            self._log(ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.error(msg, *args, exc_info = exc_info, extra=self._fill_log(), **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, extra=self._fill_log(), **kwargs)

    def success(self, message, *args, **kws):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, message, args, extra=self._fill_log(), **kws)

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, extra=self._fill_log(), **kws)

    def task(self, message, *args, **kws):
        if self.isEnabledFor(TASK):
            self._log(TASK, message, args, extra=self._fill_log(), **kws)

    logging.Logger.success = success
    logging.Logger.trace = trace
    logging.Logger.task = task
    logging.Logger.critical = critical
    logging.Logger.exception = exception
    logging.Logger.error = error
    logging.Logger.warning = warning
    logging.Logger.info = info
    logging.Logger.debug = debug
    logging.Logger._fill_log = _fill_log


_override()


def _get_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getfile(_get_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


_path = '\\'.join(_get_dir().replace('/', '\\').split('\\')[0:-1])
_path = os.path.normpath(os.path.join(_path, 'logs'))
try:
    os.makedirs(_path)
except FileExistsError:
    pass
except OSError as e:
    raise OSError(f"Ошибка создания пути {_path} к файлам логгера.", repr(e))

_format = "%(asctime)s | %(levelname)-8s | %(prefix)-8s | %(globalid)-8s | " \
              "%(threadName)-10s | %(modulename)-10s | %(funcname)-10s | %(message)s"

_formatter = logging.Formatter(_format)


def _get_file_handler(name):
    file_obj = RotatingFileHandler(os.path.join(_path, name + ".log"), maxBytes = 50000000, backupCount = 5)
    file_obj.setLevel("TRACE")
    file_obj.setFormatter(_formatter)
    return file_obj


def _get_stream_handler():
    stream_obj = logging.StreamHandler()
    stream_obj.setLevel("TRACE")
    stream_obj.setFormatter(_formatter)
    return stream_obj


def getLogger(name):
    if name:
        if not isinstance(name, str):
            raise TypeError("Имя логгера не str")
        if len(''.join(name.split())) == 0:
            raise TypeError("Имя логгера должно быть не пустой строкой.")
        if name in Loggos.logger_name_dict:
            return Loggos.logger_name_dict[name]
        log_obj = logging.getLogger(name)
        log_obj.setLevel("TRACE")
        file_obj = _get_file_handler(name)
        log_obj.addHandler(file_obj)
        stream_obj = _get_stream_handler()
        log_obj.addHandler(stream_obj)
        return Loggos(name, log_obj, file_obj, stream_obj)


class Loggos:
    logger_name_dict = {}

    def __init__(self, name, log_obj, file_obj, stream_obj):
        self.name = name
        self.log_obj = log_obj
        self.file_obj = file_obj
        self.stream_obj = stream_obj
        Loggos.logger_name_dict[name] = self

    def delIndexFormat(self, *args):
        format_list = _format.split('|')
        for i in args:
            if not isinstance(i, int):
                raise TypeError('Для удаления элементов форматирования лога укажите их индексы int через запятую.')
            try:
                format_list.pop(i)
            except IndexError:
                raise TypeError(f'Элемента форматирования лога с индексом {i} не найдено.')
        new_format = "|".join(format_list)
        self.file_obj.setFormatter(logging.Formatter(new_format))
        self.stream_obj.setFormatter(logging.Formatter(new_format))

    def setLevel(self, level):
        self.log_obj.setLevel(level)

    def setLevelFile(self, level):
        self.file_obj.setLevelFile(level)

    def setLevelStream(self, level):
        self.stream_obj.setLevelStream(level)

    def critical(self, msg, *args, **kwargs):
        self.log_obj.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log_obj.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.log_obj.exception(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log_obj.warning(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        self.log_obj.success(msg, *args, **kwargs)

    def task(self, msg, *args, **kwargs):
        self.log_obj.task(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log_obj.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.log_obj.debug(msg, *args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        self.log_obj.debug(msg, *args, **kwargs)
