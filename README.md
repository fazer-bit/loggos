
# loggos

Обёртка стандартного logging для удобного создания экземпляров логгеров .

### Лицензия
* MIT
### Инсталляция
    pip install git+https://github.com/fazer-bit/loggos.git
### Описание
Пакет loggos помогает быстро создавать экземпляры класса logging
с двумя хандлерами stream и file в каждом.

>       import loggos
>    
>       log_1 = loggos.getLogger("name1")
>       log_1.debug('сообщение первого лога')
>       log_2 = loggos.getLogger("name2")
>       log_2.trace('сообщение второго лога')
>В данном примере созданы два независимых логгера с двумя хандлерами в каждом.
>
>RotatingFileHandler пишет в директорию ..\logs\ относительно скрипта.
>
>Для каждого экземпляра loggos создаётся отдельный файл лога формата: **name.log**
>с ротацией 5 файлов по 50 Mb.
>
>StreamHandler пишет в консоль.

>       log_1 = loggos.getLogger("name1")
>       log_2 = loggos.getLogger("name1")
>Если повторно создать логгер с уже существующим именем, то вернётся объект
>уже существующего экземпляра класса, т.е.  
>
>**log_1 == log_2**

>       CRITICAL = 50
>       ERROR = 40
>       WARNING = 30
>       SUCCESS = 25
>       TASK = 23
>       INFO = 20
>       DEBUG = 10
>       TRACE = 5
>       NOTSET = 0
>Существующие уровни логгирования.

>       log = loggos.getLogger("name")
>       log.setLevel(20)
>       log.setLevelFile("SUCCESS")
>       log.setLevelStream(10)
>Для каждого экземпляра логгера можно изменить общий для его хандлеров
>уровень вывода с помощью **log.setLevel.**
>
>Либо корректировать уровень вывода каждого хандлера отдельно. 

>       import loggos
>
>       log = loggos.getLogger("NameLogger")
>       log.task('Сообщение task')
>       log.trace("Сообщение trace")
>
>       > вывод
>       > время | уровень | зарезервировано | зарезервировано | имя потока | имя фуекции | имя содуля | сообщение
>       2020-10-29 05:09:27,313 | TASK     | -----    | -----    | MainThread | <module>   | run.py     | Сообщение task
>       2020-10-29 05:09:27,314 | DEBUG    | -----    | -----    | MainThread | <module>   | run.py     | Сообщение trace
> По умолчанию вывод в оба хандлера идёт в таком формате.

>       log = loggos.getLogger("NameLogger")
>       log.task('Сообщение task')
>       log.delIndexFormat(2, 3, 5)
>       log.task('Сообщение task')
>       log.delIndexFormat()
>       log.task('Сообщение task')
>
>       > вывод
>       2020-10-29 05:50:18,644 | TASK     | -----    | -----    | MainThread | <module>   | run.py     | Сообщение task
>       2020-10-29 05:50:18,645 | TASK     | MainThread | run.py     | Сообщение task
>       2020-10-29 05:50:18,646 | TASK     | -----    | -----    | MainThread | <module>   | run.py     | Сообщение task
>Метод **delIndexFormat(2, 3, 5)** удалил поля вывода по индексам.
>
>**delIndexFormat()** без параметров возвращает формат в исходное состояние.

>       import loggos
>
>       log = loggos.getLogger("NameLogger")
>       log.debug('Сообщение debug')
>       PREF = 123
>       log.task('Сообщение task')
>       GID = 'gl_gid'
>
>       def func1():
>           GID = 'fn1_gid'
>           PREF = "fn1_pref"
>           log.success('Из функции func1')
>
>       def func2():
>           log.error('Из функции func2')
>
>       class A:
>           PREF = "cl_pref"
>           GID = 'cl_gid'
>
>       def __init__(self):
>           log.critical("Из класса")
>           self.PREF = "ins_pref"
>           log.trace("Из класса")
>
>       f1 = func1()
>       f2 = func2()
>       cl = A()
>
>       > вывод
>       2020-10-29 06:30:06,489 | DEBUG    | -----    | -----    | MainThread | <module>   | run.py     | Сообщение debug
>       2020-10-29 06:30:06,490 | TASK     | 123      | -----    | MainThread | <module>   | run.py     | Сообщение task
>       2020-10-29 06:30:06,491 | SUCCESS  | fn1_pref | fn1_gid  | MainThread | func1      | run.py     | Из функции func1
>       2020-10-29 06:30:06,491 | ERROR    | 123      | gl_gid   | MainThread | func2      | run.py     | Из функции func2
>       2020-10-29 06:30:06,492 | CRITICAL | cl_pref  | cl_gid   | MainThread | __init__   | run.py     | Из класса
>       2020-10-29 06:30:06,493 | DEBUG    | ins_pref | cl_gid   | MainThread | __init__   | run.py     | Из класса

>Два зарезервированные поля созданы для динамической вставки парметров в лог.
>
>Обязательные имена переменных PREF и GID.
>
>Поиск переменных изначально идёт в пространстве имён globals(), затем в locals() и после в экземпляре класса. 