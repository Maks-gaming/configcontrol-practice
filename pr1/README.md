# Эмулятор оболочки UNIX

Практическая работа по дисциплине «Конфигурационное управление»,
вариант 16. Выполнил: Клименко Максим.

## Общее описание

Эмулятор командной строки UNIX-подобной ОС с графическим интерфейсом
на tkinter. Пользователь вводит команды в строку ввода внизу окна,
команды и их вывод появляются в поле выше, как в терминале.

Сделаны **все 5 этапов**:

1. **REPL** - окно с заголовком `Эмулятор - [username@hostname]`
   (данные берутся из реальной ОС), парсер с раскрытием переменных
   окружения, заглушки `ls` и `cd` (на этапе 4 заменены настоящими),
   команда `exit`, сообщения об ошибках.
2. **Конфигурация** - параметры командной строки (путь к VFS и путь
   к стартовому скрипту), отладочный вывод параметров при запуске,
   выполнение стартового скрипта.
3. **VFS** - виртуальная файловая система загружается из XML-файла
   в память, двоичные данные хранятся в base64, ошибки загрузки
   сообщаются пользователю.
4. **Основные команды** - настоящие `ls` и `cd` по VFS (абсолютные
   и относительные пути, `.`, `..`, `~`), новые команды `whoami`
   и `find`.
5. **Дополнительные команды** - `rm` (файлы, `rm -r` для каталогов),
   изменения только в памяти, XML-файл VFS не меняется.

## Требования

- Python 3.8 или новее, только стандартная библиотека;
- tkinter (в Ubuntu/Debian: `sudo apt install python3-tk`).

## Запуск

Проект лежит в папке `pr1/` общего репозитория практик, все команды
ниже выполняются из нее:

```sh
git clone https://github.com/Maks-gaming/configcontrol-practice.git
cd configcontrol-practice/pr1
./run.sh [-h] [--vfs PATH] [--script PATH]
```

| Параметр        | Описание                                           |
|-----------------|----------------------------------------------------|
| `--vfs PATH`    | путь к XML-файлу VFS; без него VFS пустая          |
| `--script PATH` | стартовый скрипт, выполняется сразу после запуска  |
| `-h`, `--help`  | справка по параметрам                              |

`run.sh` можно запускать из любой папки, относительные пути
считаются от текущей папки. Интерпретатор выбирается сам:
`python3`, если он реально запускается, иначе `python`, иначе
`py -3`, поэтому `run.sh` и `scripts/*.sh` работают и в Git Bash
на Windows. Без `run.sh` то же самое делает `python3 -m src.main`
из папки `pr1/`.

### Запуск на Windows

Нужен Python 3 с python.org (tkinter входит в установщик).
В `cmd` или PowerShell из папки `pr1`:

```bat
run.bat --vfs vfs\deep.xml --script startup\stage4.txt
scripts\vfs_stage4.bat
python -m unittest discover tests
```

- `run.bat` запускает `python`, а если его нет, то `py -3`;
- у каждого `scripts\*.sh` есть `.bat`-версия с тем же именем;
- в Git Bash можно запускать и `./run.sh`, и `scripts/*.sh`;
- пути к файлам можно писать и через `\`, и через `/`.

При запуске все параметры печатаются в консоль и в окно:

```
[debug] параметры запуска:
[debug]   vfs = vfs/deep.xml
[debug]   script = startup/stage3.txt
```

## Команды эмулятора

| Команда                       | Что делает                                   |
|-------------------------------|----------------------------------------------|
| `ls [-l] [-a] [путь...]`      | содержимое каталогов или имя файла           |
| `cd [путь]`                   | сменить текущий каталог, без пути - домой    |
| `whoami`                      | имя пользователя реальной ОС                 |
| `find [путь] [-name шаблон]`  | рекурсивный поиск файлов и каталогов         |
| `rm [-r] путь...`             | удалить файлы, с `-r` также каталоги         |
| `vfs-info`                    | служебная: источник и размеры VFS            |
| `exit`                        | закрывает эмулятор                           |

### Пути и текущий каталог

- путь от корня (`/etc/motd`) или от текущего каталога
  (`docs/plan.txt`, `./docs`);
- `.` - текущий каталог, `..` - родительский (выше корня
  не поднимается, как в UNIX);
- `~` и `~/...` - домашний каталог в VFS, он выбирается так:
  `/home/<пользователь ОС>`, если такой есть, иначе первый
  по алфавиту каталог внутри `/home`, иначе корень `/`; поэтому
  эмулятор не зависит от имени пользователя в ОС;
- после загрузки VFS эмулятор переходит в домашний каталог;
- текущий каталог виден в приглашении: `maksim@laptop:~/docs$`.

### ls

- без аргументов показывает текущий каталог, можно передать
  несколько путей, тогда у каждого каталога есть заголовок `путь:`;
- имена выводятся по алфавиту, скрытые (начинаются с `.`) не видны;
- `-a` показывает скрытые файлы и записи `.` и `..`;
- `-l` подробный вывод: тип и права, размер в байтах, имя;
- опции можно склеивать: `-la`;
- для файла выводится его путь, как в UNIX.

### cd

- `cd путь` переходит в каталог, `cd` без аргумента и `cd ~` -
  в домашний каталог.

### whoami

Печатает имя пользователя ОС, в которой запущен эмулятор
(то же, что в заголовке окна).

### find

- `find` без аргументов обходит текущий каталог и печатает `.`,
  `./docs`, `./docs/plan.txt` и т.д.;
- `find путь` обходит дерево от указанного пути, пути выводятся
  с тем же началом (`find /etc` -> `/etc/motd`, `find ~` ->
  `/home/maksim/...`);
- `-name шаблон` оставляет только узлы, имя которых подходит
  под шаблон (модуль `fnmatch`): `*` - любые символы, `?` - один
  символ, `[abc]` - один из перечисленных. Шаблон лучше брать
  в кавычки: `find / -name "*.txt"`.

### rm

- `rm файл...` удаляет один или несколько файлов;
- `rm -r каталог` удаляет каталог со всем содержимым;
- все изменения только в памяти: после перезапуска VFS снова
  загружается из XML-файла в исходном виде;
- если удален текущий каталог, эмулятор переходит в родительский
  каталог удаленного.

### Ошибки

Ошибки выводятся красным цветом, тексты как в bash и GNU coreutils:

| Ситуация                      | Сообщение                                                    |
|-------------------------------|--------------------------------------------------------------|
| неизвестная команда           | `error: pwd: command not found`                              |
| лишние аргументы              | `error: cd: too many arguments`                              |
| неизвестная опция             | `error: ls: invalid option -- 'z'`                           |
| незакрытая кавычка            | `error: syntax error: No closing quotation`                  |
| `ls` нет пути                 | `error: ls: cannot access '/x': No such file or directory`   |
| `cd` нет каталога             | `error: cd: /x: No such file or directory`                   |
| `cd` в файл                   | `error: cd: /etc/motd: Not a directory`                      |
| `whoami` с аргументом         | `error: whoami: extra operand 'root'`                        |
| `find` нет пути               | `error: find: '/x': No such file or directory`               |
| `find` без шаблона            | `error: find: missing argument to '-name'`                   |
| `find` чужой предикат         | `error: find: unknown predicate '-type'`                     |
| `rm` без аргументов           | `error: rm: missing operand`                                 |
| `rm` нет пути                 | `error: rm: cannot remove '/x': No such file or directory`   |
| `rm` каталог без `-r`         | `error: rm: cannot remove 'docs': Is a directory`            |
| `rm -r /`                     | `error: rm: it is dangerous to operate recursively on '/'`   |
| `rm .` или `rm ..`            | `error: rm: refusing to remove '.' or '..' directory: ...`   |

### Парсер

- переменные окружения реальной ОС раскрываются в обеих формах:
  `$NAME` и `${NAME}`; неизвестная переменная, как в bash,
  становится пустой строкой;
- на Linux есть `$HOME` и `$USER`, на Windows `$USERPROFILE`
  и `$USERNAME`, обратная косая черта в значении сохраняется:

```
maksim@laptop:~$ ls $USERPROFILE
error: ls: cannot access 'C:\Users\maksim': No such file or directory
maksim@laptop:~$ cd /home/$USERNAME
```

- стартовые скрипты пишут `/home/$USER$USERNAME`: на Linux
  раскроется `$USER`, на Windows `$USERNAME`, вторая переменная
  станет пустой строкой;
- строка делится на слова по пробелам, текст в кавычках
  (`"my dir"` или `'my dir'`) остается одним словом.

## Стартовый скрипт

Обычный текстовый файл, одна команда эмулятора в строке.

- команды выполняются по очереди, в окне видна каждая команда
  с приглашением и ее вывод, как будто их ввел пользователь;
- пустые строки и строки, начинающиеся с `#`, пропускаются;
- строка с ошибкой не останавливает скрипт: выводится сообщение
  `файл:номер_строки: error: ...`, выполнение идет дальше;
- если файла скрипта нет, выводится `error: cannot read script ...`;
- `exit` в скрипте закрывает эмулятор.

Примеры:

| Скрипт               | Что проверяет                                       |
|----------------------|-----------------------------------------------------|
| `startup/stage2.txt` | этап 2: выполнение команд и пропуск ошибок          |
| `startup/stage3.txt` | этап 3: команды этапов 1-3, VFS и ошибки            |
| `startup/stage4.txt` | этап 4: все режимы `ls`, `cd`, `whoami`, `find`     |
| `startup/stage5.txt` | этап 5: все режимы `rm` и ошибки                    |

## Виртуальная файловая система (VFS)

VFS описывается XML-файлом. Он читается целиком в память и не
изменяется, `rm` меняет только дерево в памяти. Корневой элемент `<vfs>`, внутри каталоги `<dir>`
и файлы `<file>`, у каждого обязательный атрибут `name`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<vfs>
  <dir name="home">
    <dir name="maksim">
      <file name="notes.txt">обычный текст</file>
      <file name="data.bin" encoding="base64">AAECAwQFBgc=</file>
    </dir>
  </dir>
  <dir name="tmp"/>
</vfs>
```

- без атрибута `encoding` содержимое файла - текст в UTF-8;
- `encoding="base64"` - двоичные данные в base64 (пробелы
  и переводы строк внутри допускаются);
- имя не может быть пустым, `.`, `..` или содержать `/`, имена
  внутри одного каталога не повторяются.

Ошибки загрузки (эмулятор сообщает об ошибке и работает дальше
с пустой VFS):

| Ситуация                | Сообщение                                          |
|-------------------------|----------------------------------------------------|
| файла нет               | `error: VFS: файл не найден: vfs/no_such_file.xml` |
| битый XML               | `error: VFS: неверный формат XML: mismatched ...`  |
| корень не `<vfs>`       | `error: VFS: корневой элемент должен быть <vfs>`   |
| неверный base64         | `error: VFS: data.bin: неверные данные base64`     |

Тестовые VFS в папке `vfs/`:

| Файл              | Содержимое                                          |
|-------------------|-----------------------------------------------------|
| `minimal.xml`     | один файл в корне                                   |
| `files.xml`       | несколько файлов, один двоичный (base64)           |
| `deep.xml`        | 7 каталогов и 8 файлов, 4 уровня каталогов          |
| `bad_xml.xml`     | ошибка: незакрытый тег                              |
| `bad_root.xml`    | ошибка: корневой элемент не `<vfs>`                 |
| `bad_base64.xml`  | ошибка: неверные данные base64                      |

## Скрипты для проверки (scripts/)

Скрипты ОС, каждый запускает эмулятор один или несколько раз
(следующий запуск начинается после закрытия окна). Рядом с каждым
`.sh` лежит `.bat` с тем же именем для Windows:

| Скрипт                | Что проверяет                                    |
|-----------------------|--------------------------------------------------|
| `params_basic.sh`     | `--help` и запуск без параметров                 |
| `params_script.sh`    | только `--script`: рабочий и несуществующий файл |
| `params_all.sh`       | оба параметра в формах `--opt x` и `--opt=x`     |
| `vfs_minimal.sh`      | минимальная VFS + `startup/stage3.txt`           |
| `vfs_files.sh`        | VFS с несколькими файлами + `startup/stage3.txt` |
| `vfs_deep.sh`         | VFS с 4 уровнями + `startup/stage3.txt`          |
| `vfs_errors.sh`       | все ошибки загрузки VFS                          |
| `vfs_stage4.sh`       | VFS с 4 уровнями + `startup/stage4.txt`          |
| `vfs_stage5.sh`       | VFS с 4 уровнями + `startup/stage5.txt`          |

## Примеры использования

Интерактивная работа (`./run.sh --vfs vfs/deep.xml`), в VFS есть
домашний каталог `/home/maksim`:

```
VFS loaded: vfs/deep.xml
maksim@laptop:~$ whoami
maksim
maksim@laptop:~$ ls -a
.
..
.profile
docs
maksim@laptop:~$ cd docs/reports
maksim@laptop:~/docs/reports$ ls
stage1.txt
stage2.txt
stage3.txt
maksim@laptop:~/docs/reports$ cd ../../..
maksim@laptop:/home$ ls -l /etc
-rw-r--r--      8 hostname
-rw-r--r--     52 motd
maksim@laptop:/home$ cd /etc/motd
error: cd: /etc/motd: Not a directory
maksim@laptop:/home$ cd
maksim@laptop:~$ find / -name "*.txt"
/home/maksim/docs/plan.txt
/home/maksim/docs/reports/stage1.txt
/home/maksim/docs/reports/stage2.txt
/home/maksim/docs/reports/stage3.txt
maksim@laptop:~$ find -name "[ps]*"
./docs/plan.txt
./docs/reports/stage1.txt
./docs/reports/stage2.txt
./docs/reports/stage3.txt
maksim@laptop:~$ find /nope
error: find: '/nope': No such file or directory
maksim@laptop:~$ exit
```

Удаление (`./run.sh --vfs vfs/deep.xml`):

```
maksim@laptop:~$ rm docs/plan.txt /etc/motd
maksim@laptop:~$ ls /etc
hostname
maksim@laptop:~$ rm docs/reports
error: rm: cannot remove 'docs/reports': Is a directory
maksim@laptop:~$ rm -r docs/reports
maksim@laptop:~$ ls -a docs
.
..
maksim@laptop:~$ cd /tmp
maksim@laptop:/tmp$ rm -r /tmp
maksim@laptop:/$ rm -r /
error: rm: it is dangerous to operate recursively on '/'
maksim@laptop:/$ vfs-info
source: vfs/deep.xml
dirs: 5, files: 3
size: 55 bytes, depth: 3
```

В стартовом скрипте перед ошибкой стоит имя файла и номер строки
(`./scripts/vfs_stage4.sh`, фрагмент):

```
maksim@laptop:~/docs$ cd /nope
startup/stage4.txt:31: error: cd: /nope: No such file or directory
maksim@laptop:~/docs$ find / -type f
startup/stage4.txt:39: error: find: unknown predicate '-type'
maksim@laptop:~/docs$ cd
maksim@laptop:~$ ls
docs
```

Ошибка загрузки VFS (`./run.sh --vfs vfs/bad_root.xml`):

```
[debug] параметры запуска:
[debug]   vfs = vfs/bad_root.xml
[debug]   script = None
error: VFS: корневой элемент должен быть <vfs>
```

## Тесты

Из папки `pr1/`:

```sh
python3 -m unittest discover tests
```

Тесты не открывают окно, поэтому работают и без дисплея:

- `tests/test_parser.py` - разбор строк, кавычки, `$HOME` и `${HOME}`,
  пути Windows в переменных;
- `tests/test_shell.py` - приглашение, выбор домашнего каталога, `exit`, ошибки команд,
  `ls`, `cd`, `whoami`, `find` (все пути и ошибки);
- `tests/test_rm.py` - `rm` файлов и каталогов, ошибки, XML-файл
  после удаления не меняется, скрипт этапа 5;
- `tests/test_config.py` - параметры командной строки и выполнение
  стартового скрипта (пропуск ошибочных строк, `exit`, нет файла);
- `tests/test_vfs.py` - загрузка всех тестовых VFS, base64,
  неизменность исходного файла, ошибки загрузки, скрипты
  этапов 3 и 4.

## Проверка стиля (PEP8)

Код в `src/` и `tests/` проходит pycodestyle и flake8 без замечаний
(строки до 79 символов, цикломатическая сложность не больше 10):

```sh
python3 -m pip install --user pycodestyle flake8
python3 -m pycodestyle src tests
python3 -m flake8 --max-complexity 10 src tests
```

Обе команды ничего не выводят, если замечаний нет.

## Структура проекта

Все пути от папки `pr1/`:

```
run.sh, run.bat   запуск эмулятора (Linux/Git Bash, Windows)
src/main.py       точка входа
src/config.py     параметры командной строки
src/gui.py        окно tkinter
src/shell.py      логика оболочки: команды и стартовый скрипт
src/parser.py     разбор строки, переменные окружения
src/vfs.py        загрузка VFS из XML
startup/          стартовые скрипты эмулятора
scripts/          скрипты ОС для запуска с разными параметрами
vfs/              тестовые VFS
tests/            тесты unittest
```
