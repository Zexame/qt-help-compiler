import os
import logging
import yaml

DEFAULT_CONFIG = {
    "qt_bin_path": "",
    "qhp_file": "",
    "qhcp_file": "",
    "output_file": "",
    "docs_root": "./docs",
    "internal": False,
    "verbose": False,
    "keep_temp": False
}

CONFIG_TEMPLATE = """# Qt Help Compiler - Конфигурационный файл

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
# true - оставить internal, false - удалить
internal: false

# Подробный вывод (аналог --verbose)
verbose: false

# Не удалять временные файлы (аналог --keep-temp)
keep_temp: false
"""


def load_config(config_path):
    config = DEFAULT_CONFIG.copy()
    
    if not os.path.exists(config_path):
        logging.warning(f"Конфиг не найден: {config_path}")
        logging.info("Используются значения по умолчанию")
        logging.info("Создайте конфиг: python main.py --generate-config")
        return config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
        
        if user_config is None:
            logging.warning(f"Конфиг пуст: {config_path}")
            return config
        
        for key, value in user_config.items():
            if key in config:
                config[key] = value
            else:
                logging.warning(f"Неизвестный ключ в конфиге: {key}")
        
        logging.debug(f"Конфиг загружен: {config_path}")
        return config
        
    except yaml.YAMLError as e:
        logging.error(f"Ошибка парсинга YAML: {e}")
        return config
    except Exception as e:
        logging.error(f"Ошибка загрузки конфига: {e}")
        return config


def merge_with_args(config, args):
    mapping = {
        'qt_bin_path': 'qt_bin',
        'qhp_file': 'qhp',
        'qhcp_file': 'qhcp',
        'output_file': 'output',
        'docs_root': 'docs_root',
        'internal': 'internal',
        'verbose': 'verbose',
        'keep_temp': 'keep_temp'
    }
    
    for config_key, args_key in mapping.items():
        if config_key in config:
            current = getattr(args, args_key, None)
            if current is None or current == '' or current is False:
                setattr(args, args_key, config[config_key])
    
    return args


def create_default_config(config_path):
    if os.path.exists(config_path):
        logging.warning(f"Файл уже существует: {config_path}")
        return False
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(CONFIG_TEMPLATE)
        
        logging.info(f"Конфиг создан: {config_path}")
        return True
    except Exception as e:
        logging.error(f"Ошибка создания конфига: {e}")
        return False