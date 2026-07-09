import os
import shutil
import logging
import tempfile


def setup_logging(verbose=False):
    """Настраивает вывод логов в консоль."""
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    level = logging.DEBUG if verbose else logging.INFO

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)

    root.addHandler(console)
    root.setLevel(level)

    # тишина для сторонних библиотек
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def find_qhelpgenerator(qt_bin_path=None):
    """
    Возвращает путь к qhelpgenerator.
    Приоритет: --qt-bin > QT_BIN_PATH > PATH.
    """
    exe = "qhelpgenerator" + (".exe" if os.name == "nt" else "")

    if qt_bin_path:
        candidate = os.path.join(qt_bin_path, exe)
        if os.path.exists(candidate):
            logging.debug(f"qhelpgenerator по --qt-bin: {candidate}")
            return candidate
        logging.warning(f"qhelpgenerator не найден по --qt-bin: {candidate}")

    env_path = os.environ.get("QT_BIN_PATH")
    if env_path:
        candidate = os.path.join(env_path, exe)
        if os.path.exists(candidate):
            logging.debug(f"qhelpgenerator по QT_BIN_PATH: {candidate}")
            return candidate
        logging.warning(f"qhelpgenerator не найден по QT_BIN_PATH: {candidate}")

    which_result = shutil.which(exe)
    if which_result:
        logging.debug(f"qhelpgenerator в PATH: {which_result}")
        return which_result

    raise FileNotFoundError(
        "qhelpgenerator не найден.\n"
        "Укажите путь в config.yaml, через --qt-bin, "
        "или добавьте в PATH."
    )


def create_temp_dir():
    """Создаёт временную папку."""
    temp_dir = tempfile.mkdtemp(prefix="qt_help_")
    logging.debug(f"Временная папка: {temp_dir}")
    return temp_dir


def clean_temp_dir(temp_dir):
    """Удаляет временную папку."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        logging.debug(f"Удалена временная папка: {temp_dir}")