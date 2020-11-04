import logging
import inspect


def update(level_dict):
    """Переопределение переменных и методов."""
    CRITICAL = level_dict['CRITICAL']
    ERROR = level_dict['ERROR']
    WARNING = level_dict['WARNING']
    SUCCESS = level_dict['SUCCESS']
    TASK = level_dict['TASK']
    INFO = level_dict['INFO']
    DEBUG = level_dict['DEBUG']
    TRACE = level_dict['TRACE']
    NOTSET = level_dict['NOTSET']

    logging.CRITICAL = CRITICAL
    logging.ERROR = ERROR
    logging.WARNING = WARNING
    logging.SUCCESS = SUCCESS
    logging.TASK = TASK
    logging.INFO = INFO
    logging.DEBUG = DEBUG
    logging.TRACE = TRACE
    logging.NOTSET = NOTSET

    logging.addLevelName(SUCCESS, "SUCCESS")
    logging.addLevelName(TRACE, "TRACE")
    logging.addLevelName(TASK, "TASK")


    def extra_log(self):
        """
        Функция автоматического заполнения extra.
        :param self:
        :return: dict
        """
        self.c_new_extra = self.new_extra.copy()
        self.extra = {}
        res = inspect.stack()[3][0]
        fl_name = res.f_code.co_filename.replace('/', '\\').split('\\')[-1]
        if fl_name.count(".") > 0:
            mod = '.'.join(fl_name.split('.')[0:-1])
        else:
            mod = fl_name
        func = res.f_code.co_name
        loc = locals().copy()
        self.extra = self.c_new_extra.copy()
        for key in self.c_new_extra:
            if key[0] != "*":
                self.extra[key] = loc[key]
            else:
                var = key[1:]
                if var in res.f_globals:
                    self.extra[key] = res.f_globals[var]
                if var in res.f_locals:
                    self.extra[key] = res.f_locals[var]
                if "self" in res.f_locals:
                    self_obj = res.f_locals["self"]
                    if hasattr(self_obj, var):
                        self.extra[key] = getattr(self_obj, var)
        return self.extra

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, extra=self.extra_log(), **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, extra=self.extra_log(), **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, extra=self.extra_log(), **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            if 'extra' not in kwargs:
                kwargs['extra'] = self.extra_log()
            self._log(ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.error(msg, *args, exc_info = exc_info, extra=self.extra_log(), **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, extra=self.extra_log(), **kwargs)

    def success(self, message, *args, **kws):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, message, args, extra=self.extra_log(), **kws)

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, extra=self.extra_log(), **kws)

    def task(self, message, *args, **kws):
        if self.isEnabledFor(TASK):
            self._log(TASK, message, args, extra=self.extra_log(), **kws)

    logging.Logger.success = success
    logging.Logger.trace = trace
    logging.Logger.task = task
    logging.Logger.critical = critical
    logging.Logger.exception = exception
    logging.Logger.error = error
    logging.Logger.warning = warning
    logging.Logger.info = info
    logging.Logger.debug = debug
    logging.Logger.extra_log = extra_log
