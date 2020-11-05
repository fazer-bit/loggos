#  ----------------------------------------------------------------------------
#  loggos
#  ----------------------------------------------------------------------------
"""
Модуль loggos является обёрткой расширяющей возможности logging.
    - При создании нового логгера с помощью функции getLogger(name)
        создаются два хандлера: RotatingFileHandler, StreamHandler.
        Запись логов ведётся в файл директории относительно скрипта ..\logs\nameLog.log
        Каждый экземпляр лога создаёт собственный файл.
        StreamHandler - отвечает за вывод в консоль.
    - Если вводимое имя уже зарегистрировано в логгере, то возвращается
        существующий объект, если нет, то создаётся новый.
    - Управление уровнями логгирования возможно для каждого хандлера
        по отдельности или всеми вместе с помощью методов:
            setLevel(level)
            setLevelFile(level)
            setLevelStream(level)
    - Реализована возможность динамического изменения формата вывода логов,
        методом:
            setFormat(fmt)
        '...' - новый формат, '' - вывод сообщения без форматирования, None - загрузка дефолтного формата.
        Новый формат действует на оба хандлера.
    - К существующим добавлены новые уровни логгирования: 'TRACE', 'TASK', 'SUCCESS'.
        Все уровни:
            'CRITICAL': 50
            'ERROR': 40
            'WARNING': 30
            'SUCCESS': 25
            'TASK': 23
            'INFO': 20
            'DEBUG': 10
            'TRACE': 5
            'NOTSET': 0
    - Сохранены, существующие в logging, поля форматирования:
        'asctime', 'created', 'name', 'levelname', 'msecs', 'levelno', 'lineno',
        'processName', 'process', 'threadName', 'thread', 'relativeCreated',
        'pathname': 'pathname', 'module', 'filename', 'funcName', 'message'
    - Изменения в % - форматировании.
        Формат поля имеет вид: '%(имя)s'. Все поля передаются в строковом виде
            с символом 's' на конце.
        пример: "%(name)-10s | %(levelname)s | %(message)7s"
    - Реализована возможность автоматического логгирования переменных из выполняемого кода
        Для этого перед именем переменной ставится '*'.
        пример: "%(name)s | %(*foo)-8s | %(levelname)s | %(message)-10s | %(*var_1)s"
        В данном случае из кода будут автоматически извлечены значения переменных
            с именами 'foo' и 'var_1'
        Поиск имен переменных в модуле ведётся согласно иерархии:
            globals() -> locals() -> self-атрибуты.
            Если переменная не найдена, то выводится: '-----'
"""

import logging
import inspect
from logging.handlers import RotatingFileHandler
from loggos._overload import update
import ast
import sys
import re
import os

__all__ = ["getLogger"]


class LoggosError(Exception):
    pass


_levels_dict = {'CRITICAL': 50,
                'ERROR': 40,
                'WARNING': 30,
                'SUCCESS': 25,
                'TASK': 23,
                'INFO': 20,
                'DEBUG': 10,
                'TRACE': 5,
                'NOTSET': 0}

update(_levels_dict)


"""Создание пути для файлов логгера: ..\\logs"""
try:
    _last_frame = inspect.stack()[-1][0]
    _path_file = _last_frame.f_code.co_filename
    _path = os.path.normpath(os.path.join(os.path.dirname(_path_file), 'logs'))
    os.makedirs(_path)
except FileExistsError:
    pass
except OSError as e:
    raise OSError(f"Ошибка создания пути {_path} к файлам логгера.", e)

"""Дефолтный формат вывода."""
_format_default = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

"""Словарь соответствия для подмены полей форматирования Loggos на logging."""
_loggos_field = {
    'asctime': 'asctime',
    'created': 'created',
    'name': 'name',
    'levelname': 'levelname',
    'msecs': 'msecs',
    'levelno': 'levelno',
    'lineno': 'lineno',
    'processName': 'processName',
    'process': 'process',
    'threadName': 'threadName',
    'thread': 'thread',
    'relativeCreated': 'relativeCreated',
    'pathname': 'pathname',
    'module': 'mod',
    'filename': 'fl_name',
    'funcName': 'func',
    'message': 'message'
    }


def _check_format(log_obj, fmt):
    """
    Функция проверки строки форматированного вывода.
    Запускается при изменении или первичной загрузке форматов.
    Автоматически подменяет ключевые поля на понятные logging.
    Создаёт и экспортирует в logging словарь extra для автозамены.
    :param log_obj:
    :param fmt: str
    :return: str - преобразованный формат.
    """
    re_field = r"%\([*]?[a-zA-Z0-9_]+\)(?:|[-+]?[0-9]+|[0-9]*)s"
    re_bub = r"(?<=%\()[a-zA-Z0-9*_]+(?=\))"
    if not isinstance(fmt, str):
        raise LoggosError("Формат логгера не str.")
    if fmt == '':
        log_obj.new_extra = {}
        return fmt
    if len(''.join(fmt.split())) == 0:
        if len(fmt) > 0:
            raise LoggosError("Формат логгера должен быть '' или иметь паттерны. "
                              "Примеры: '%(name)s , %(*val)-5s , %(*_foo)10s'")
    else:
        num_re = len(re.findall(re_field, fmt))
        num = fmt.count('%')
        if num_re == 0 or num != num_re:
            raise LoggosError("Паттерны логгера нарушают правила % форматирования. "
                              "Примеры: '%(name)s , %(*val)-5s , %(*_foo)10s'.")
    fields = re.findall(re_bub, fmt)
    sub_fields = re.split(re_bub, fmt, maxsplit = 0)
    new_format_list = []
    new_extra = {}
    for ind, sub_val in enumerate(sub_fields):
        new_format_list.append(sub_val)
        try:
            fld = fields[ind]
        except IndexError:
            break
        if fld[0] == '*':
            fld_1 = fld[1:]
            try:
                ast.parse(f'{fld_1} = True')
            except (SyntaxError, ValueError, TypeError, NameError):
                raise LoggosError(f"Поле логгера: '{fld_1}' не может быть именем переменной.")
            new_format_list.append(fld)
            new_extra[fld] = '-----'
        else:
            flag = 0
            for key, val in _loggos_field.items():
                if fld == key:
                    if fld in ['filename', 'funcName', 'module']:
                        new_extra[val] = '-----'
                    new_format_list.append(val)
                    flag = 1
            if flag == 0:
                raise LoggosError(f"Поле логгера '{fld}' не является "
                                  f"допустимым: {', '.join(_loggos_field.keys())}.")
    new_format = ''.join(new_format_list)
    log_obj.new_extra = new_extra
    return new_format


def _get_file_handler(name):
    """
    Создание файлового хандлера.
    Ротация 5 файлов по 50 мегабайт.
    """
    file_obj = RotatingFileHandler(os.path.join(_path, name + ".log"), maxBytes = 50000000, backupCount = 5)
    file_obj.setLevel("TRACE")
    return file_obj


def _get_stream_handler():
    """ Создание консольного хандлера."""
    stream_obj = logging.StreamHandler(sys.stdout)
    stream_obj.setLevel("TRACE")
    return stream_obj


def getLogger(name):
    """
    Функция создания нового логгера. Вынесена из класса для соблюдения стандарта logging.
    import loggos
    loggos.getLogger(str) - формат вызова
    Если вводимое имя уже зарегистрировано в логгере, то возвращается существующий логгер.
    :param name: str, имя логгера
    :return: объекты логгера и хандлеров
    """
    if not isinstance(name, str):
        raise LoggosError("Имя логгера не str")
    if len(''.join(name.split())) == 0:
        raise LoggosError("Имя логгера должно быть не пустой строкой.")
    if name in Loggos.logger_name_dict:
        return Loggos.logger_name_dict[name]
    log_obj = logging.getLogger(name)
    log_obj.setLevel("TRACE")
    file_obj = _get_file_handler(name)
    stream_obj = _get_stream_handler()
    new_format = _check_format(log_obj, _format_default)
    formatter_obj = logging.Formatter(new_format)
    file_obj.setFormatter(formatter_obj)
    stream_obj.setFormatter(formatter_obj)
    log_obj.addHandler(file_obj)
    log_obj.addHandler(stream_obj)
    log_obj.propagate = False
    return Loggos(name, log_obj, file_obj, stream_obj)


def _check_levels(level, obj_lvl):
    """
    Проверка введённого уровня для основного логгера, файлового и консольного.
    :param level: str, int
    :param obj_lvl: ссылка на функцию
    :return: None
    """
    if not isinstance(level, (int, str)):
        raise LoggosError("Тип уровня логгера должен быть str или int")
    try:
        obj_lvl(level)
    except (ValueError, TypeError, AttributeError):
        raise LoggosError(f"Уровень может быть ключом или значением: {','.join(_levels_dict)}")


class Loggos:
    """
    Основной класс логгера.
    Создаются и запускаются два хандлераб файловый и консольный.
        Файловый пишет в отдельный файл ..\logs\имя логгера.log.
    Для управления выводом необходимо изменить уровень логгера или хандлеров по отдельности.
    Полностью дублирует основные функции logging в плане отправки сообщений.
    setLevel(self, level) - изменение уровня логгирования для всех хандлеров.
    setLevelFile(self, level) - для файлового хандлера.
    setLevelStream(self, level) - для консольного.
    """
    logger_name_dict = {}

    def __init__(self, name, log_obj, file_obj, stream_obj):
        self.name = name
        self.log_obj = log_obj
        self.file_obj = file_obj
        self.stream_obj = stream_obj
        Loggos.logger_name_dict[name] = self

    def setFormat(self, fmt=None):
        """
        Изменение форматирования налету.
        '...' - новый формат, '' - вывод сообщения без форматирования, None - загрузка дефолтного формата.
        :param fmt: str, None
        :return:
        """
        if isinstance(fmt, str):
            new_format = _check_format(self.log_obj, fmt)
        else:
            new_format = _check_format(self.log_obj, _format_default)
        formatter_obj = logging.Formatter(new_format)
        self.file_obj.setFormatter(formatter_obj)
        self.stream_obj.setFormatter(formatter_obj)

    def setLevel(self, level):
        """
        Изменение уровня логгирования для всех хандлеров.
        :param level: str, int
        :return:
        """
        _check_levels(level, self.log_obj.setLevel)

    def setLevelFile(self, level):
        """
        Изменение уровня логгирования для файлового хандлера.
        :param level: str, int
        :return:
        """
        _check_levels(level, self.file_obj.setLevel)

    def setLevelStream(self, level):
        """
        Изменение уровня логгирования для консольного хандлера.
        :param level: str, int
        :return:
        """
        _check_levels(level, self.stream_obj.setLevel)

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
        self.log_obj.trace(msg, *args, **kwargs)
