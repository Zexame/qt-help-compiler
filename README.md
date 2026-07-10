# Qt Help Compiler

Инструмент для автоматической сборки справочной документации в формате Qt Assistant (`.qhc`) с дополнительным препроцессингом.

## Возможности

- **Поддержка атрибута `path`** - копирование HTML-файлов из произвольных папок в структуру проекта.
- **Фильтрация `internal`** - автоматическое удаление секций и ключевых слов с атрибутом `internal="yes"` (режим `-i` для сохранения).
- **Объединение `.qhp`** - встраивание содержимого нескольких `.qhp` файлов в один корневой (рекурсивно).
- **Автоматическое сканирование HTML** - режим `--find-html` для быстрой генерации структуры `.qhp` по существующим файлам.
- **Конфигурация через YAML** - настройка путей и флагов в читаемом формате с комментариями.
- **Гибкий запуск** - аргументы командной строки имеют приоритет над конфигом.

## Требования

- Python 3.8+
- Установленный Qt (с утилитой `qhelpgenerator.exe` в папке `bin`)
- Библиотеки из `requirements.txt`

## Установка

```bash
git clone https://github.com/Zexame/qt-help-compiler.git
cd qt-help-compiler
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows
pip install -r requirements.txt
```

## Конфигурация

Создайте `config.yaml` в корне проекта:

```yaml
# Путь к папке bin с утилитами Qt
qt_bin_path: "C:/Qt/6.11.1/mingw_64/bin"

# Путь к .qhp файлу
qhp_file: "help.qhp"

# Путь к .qhcp файлу
qhcp_file: "collection.qhcp"

# Путь для сохранения результата
output_file: "build/help.qhc"

# Корневая папка с документацией (для --find-html)
docs_root: "./docs"

# Собрать внутреннюю документацию (аналог -i)
internal: false

# Подробный вывод (аналог --verbose)
verbose: false

# Не удалять временные файлы (аналог --keep-temp)
keep_temp: false
```

Или запустите скрипт с флагом `--generate-config` для создания конфига по умолчанию:

```bash
python main.py --generate-config
```
## Использование

### Базовый запуск

```bash
python main.py
```

### С флагом внутренней документации

```bash
python main.py -i
```

### Режим сканирования HTML

```bash
python main.py --find-html --docs-root ./docs
```

Если путь к папке с документацией указан в конфиге:
```bash
python main.py --find-html
```

Результат сохраняется в `html_find_out/html_scan_YYYYMMDD_HHMMSS.txt`.

### Переопределение параметров

```bash
python main.py --output custom.qhc --verbose
```

### Использование другого конфига

```bash
python main.py --config production.yaml
```
## Структура проекта

```
.
├── main.py                 # Точка входа
├── preprocessor.py         # Загрузка, парсинг, модификация .qhp
├── qhp_merger.py           # Объединение нескольких .qhp
├── qhelpgenerator_wrapper.py # Запуск qhelpgenerator
├── html_scanner.py         # Сканирование HTML-файлов
├── config_manager.py       # Работа с YAML-конфигом
├── utils.py                # Вспомогательные функции
├── config.yaml             # Конфигурационный файл
├── requirements.txt        # Зависимости
└── README.md               # Документация
```

## Как это работает

1. Загружается `.qhp` файл.
2. Если не указан флаг `-i` - удаляются все элементы с `internal="yes"`.
3. Обрабатываются атрибуты `path`: файлы копируются из указанных путей в структуру `ref`.
4. Происходит объединение вложенных `.qhp` файлов (если есть).
5. Сохраняется временный `.qhp` и запускается `qhelpgenerator`.
6. На выходе - готовый `.qhc` файл.

## Аргументы командной строки

| Аргумент            | Описание                                                  |
| ------------------- | --------------------------------------------------------- |
| `--qhp`             | Путь к .qhp файлу                                         |
| `--qhcp`            | Путь к .qhcp файлу                                        |
| `--output`          | Путь для сохранения результата                            |
| `-i, --internal`    | Сохранить internal-секции (по умолчанию удаляются)        |
| `--qt-bin`          | Путь к папке bin с утилитами Qt                           |
| `-c, --config`      | Путь к конфигурационному файлу (по умолчанию config.yaml) |
| `--generate-config` | Создать конфиг со значениями по умолчанию                 |
| `-v, --verbose`     | Подробный вывод                                           |
| `--keep-temp`       | Не удалять временные файлы                                |
| `--find-html, -fh`  | Режим сканирования HTML-файлов                            |
| `--docs-root`       | Корневая папка с документацией                            |

## Особенности

### Атрибут `path`

Позволяет указать реальное расположение файла в репозитории:

```xml
<section title="Объединение проектов"
         ref="db/objects/mergeObjects.html"
         path="../somerandompath/mergeObjects.html"/>
```

Скрипт скопирует файл из `path` в `ref` и удалит атрибут `path` из XML.

### Internal-секции

```xml
<section title="Внутренний раздел" ref="internal.html" internal="yes"/>
```

Без флага `-i` такие секции удаляются. С флагом `-i` - сохраняются.

### Объединение .qhp

```xml
<section title="Базы Данных" ref="db/another.qhp"/>
```

Скрипт загрузит `another.qhp` и встроит его содержимое в корневой файл.

## Возможные ошибки

### `qhelpgenerator не найден`

Укажите путь в `config.yaml` или через `--qt-bin`.

### `Файл не найден`

Проверьте, что все файлы из `<files>` существуют и указаны в `path`.

## Лицензия

MIT

## Контакты
По вопросам: 
Repin2005@yandex.ru
[GitHub](https://github.com/Zexame)
[TG](https://t.me/Zexame)

