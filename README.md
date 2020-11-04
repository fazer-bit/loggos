
# loggos

Модуль loggos является обёрткой расширяющей возможности logging.
### Лицензия
* MIT
### Инсталляция
    pip install git+https://github.com/fazer-bit/loggos.git
### Описание
Создание логгера.

    - При создании нового логгера с помощью функции getLogger(name),
        создаются два хандлера: RotatingFileHandler, StreamHandler.
        Запись файлов логов ведётся директорию относительно скрипта ..\logs\nameLog.log
        Каждый экземпляр лога создаёт собственный файл.
        StreamHandler - отвечает за вывод в консоль.
пример:
    
    import loggos

    log1 = loggos.getLogger("myLog_1")
    log1.debug("Сообщение debug myLog_1")
    log2 = loggos.getLogger("myLog_2")
    log2.debug("Сообщение debug myLog_2")
            
    >>> 2020-11-04 22:35:48,429 | myLog_1 | DEBUG | Сообщение debug myLog_1
    >>> 2020-11-04 22:35:48,431 | myLog_2 | DEBUG | Сообщение debug myLog_2

>

    Параллельно с выводом в консоль созданы два файла логов:
    myLog_1.log и myLog_2 в директории ..\logs\
---  
Имена логгеров.
  
    - Если вводимое имя уже зарегистрировано в логгере, то возвращается 
        существующий объект, если нет, то создаётся новый.

пример:
        
    log1 = loggos.getLogger("myLog_1")
    log2 = loggos.getLogger("myLog_1")
    log3 = loggos.getLogger("myLog_3")
    print(log1)
    print(log2)
    print(log3)
    
    >>> <loggos.Loggos object at 0x00000205939DCC40>
    >>> <loggos.Loggos object at 0x00000205939DCC40>
    >>> <loggos.Loggos object at 0x00000205939DCD00>
---
Уровни логгирования.

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

    - Управление уровнями логгирования возможно для каждого хандлера
        по отдельности или всеми вместе с помощью методов:
            setLevel(level)
            setLevelFile(level)
            setLevelStream(level)
        Указание уровней возможно в виде текста или целого числа.
    
пример:

    log = loggos.getLogger("myLog")
    log.setLevel(30)
    log.setLevelFile("WARNING")
    log.setLevelStream("DEBUG")
---

Форматирование.

    - Сохранены существующие в logging поля форматирования:
        'asctime', 'created', 'name', 'levelname', 'msecs', 'levelno', 'lineno',
        'processName', 'process', 'threadName', 'thread', 'relativeCreated',
        'pathname': 'pathname', 'module', 'filename', 'funcName', 'message'
    
    - Изменения в % - форматировании.
        Формат поля имеет вид: '%(имя)s'. Все поля передаются в строковом виде
            с символом 's' на конце.
        пример: "%(name)-10s | %(levelname)s | %(message)7s"
    
    - Реализована возможность динамического изменения формата вывода логов,
        методом:
            setFormat(fmt)
        '...' - новый формат, '' - вывод сообщения без форматирования, None - загрузка дефолтного формата.
        Обновления действуют на оба хандлера.

пример:

    log = loggos.getLogger("myLog")
    log.info("Сообщение дефолтного фармата.")
    log.setFormat("%(levelname)s, %(module)-10s, %(filename)-10s, %(funcName)-10s, %(name)-10s, %(message)s")
    log.info("Сообщение нового фармата.")
    log.setFormat('')
    log.info("Только сообщение без форматирования.")
    log.setFormat()
    log.info("Сброс к дефолтному формату.")
    
    >>> 2020-11-04 23:08:40,728 | myLog | INFO | Сообщение дефолтного фармата.
    >>> INFO, read      , read.py   , <module>  , myLog     , Сообщение нового фармата.
    >>> Только сообщение без форматирования.
    >>> 2020-11-04 23:08:40,730 | myLog | INFO | Сброс к дефолтному формату.
   
---
   
Динамическое логгирование переменных кода.
   
    - Реализована возможность автоматического логгирования переменных из выполняемого кода
        Для этого перед именем переменной ставится '*'.
        пример: "%(name)s | %(*foo)-8s | %(levelname)s | %(message)-10s | %(*var_1)s"
        В данном случае из кода будут автоматически извлечены значения переменных
            с именами 'foo' и 'var_1'
        Поиск имен переменных в модуле ведётся согласно иерархии:
            globals() -> locals() -> self-атрибуты.
            Если переменная не найдена, то выводится: '-----'

пример:

    var = "var_glb"
    log = loggos.getLogger("myLog")
    log.setFormat("%(levelname)-8s | %(*foo)-8s | %(*bar)-8s | %(*var)-8s | %(message)s")
    log.info("mes1")
    foo = 123
    log.info("mes2")

    def func():
    bar = "bar_f"
    foo = "foo_f"
    log.info("mes3")

    class A:
        var = "var_cls"
        log.info("mes4")

        def __init__(self):
            self.var = "var_slf"
            self.foo = "foo_slf"
            log.info("mes5")

        def mtd1(self):
            self.bar = "bar_slf"
            log.info("mes6")

        def mtd2(self):
            log.info("mes7")

    func()
    a = A()
    a.mtd1()
    a.mtd2()
    
    >>> INFO     | -----    | -----    | var_glb  | mes1
    >>> INFO     | 123      | -----    | var_glb  | mes2
    >>> INFO     | 123      | -----    | var_cls  | mes4
    >>> INFO     | foo_f    | bar_f    | var_glb  | mes3
    >>> INFO     | foo_slf  | -----    | var_slf  | mes5
    >>> INFO     | foo_slf  | bar_slf  | var_slf  | mes6
    >>> INFO     | foo_slf  | bar_slf  | var_slf  | mes7
