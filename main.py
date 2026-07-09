import sys
import os
import argparse
import logging

from preprocessor import QHPPreprocessor
from qhelpgenerator_wrapper import QHelpGeneratorWrapper
from qhp_merger import QHPMerger
from utils import setup_logging, find_qhelpgenerator
from config_manager import load_config, merge_with_args, create_default_config
from html_scanner import scan_html_files


def validate_inputs(args):
    errors = []
    
    if not os.path.exists(args.qhp):
        errors.append(f".qhp файл не найден: {args.qhp}")
    
    if not os.path.exists(args.qhcp):
        errors.append(f".qhcp файл не найден: {args.qhcp}")
    
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logging.info(f"Создана выходная директория: {output_dir}")
            except Exception as e:
                errors.append(f"Не удалось создать выходную директорию: {e}")
    
    if args.qt_bin:
        qhelp_path = os.path.join(args.qt_bin, "qhelpgenerator" + (".exe" if os.name == "nt" else ""))
        if not os.path.exists(qhelp_path):
            errors.append(f"qhelpgenerator не найден по пути: {qhelp_path}")
    
    if errors:
        for error in errors:
            logging.error(error)
        return False
    
    return True


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Инструмент для компиляции справочной информации для QtAssistant",
        epilog="Примеры:\n"
               "  python main.py --qhp help.qhp --qhcp collection.qhcp --output help.qhc\n"
               "  python main.py --find-html --docs-root ./docs\n"
               "  python main.py --config config.yaml"
    )
    
    parser.add_argument(
        "--find-html", "-fh",
        action="store_true",
        help="Режим поиска HTML-файлов (генерирует строки для .qhp)"
    )
    
    parser.add_argument(
        "--docs-root",
        help="Корневая папка с документацией"
    )
    
    parser.add_argument(
        "--qhp",
        help="Путь к .qhp файлу"
    )
    
    parser.add_argument(
        "--qhcp",
        help="Путь к .qhcp файлу"
    )
    
    parser.add_argument(
        "--output",
        help="Путь для сохранения результата (help.qhc)"
    )
    
    parser.add_argument(
        "-i", "--internal",
        action="store_true",
        help="Собрать внутреннюю документацию (аналог -i)"
    )
    
    parser.add_argument(
        "--qt-bin",
        help="Путь к папке bin с утилитами Qt"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Путь к конфигурационному файлу (по умолчанию config.yaml)"
    )
    
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Создать конфиг-файл со значениями по умолчанию"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Подробный вывод"
    )
    
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Не удалять временные файлы"
    )
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    if args.generate_config:
        setup_logging(False)
        create_default_config(args.config)
        return

    setup_logging(False)
    config = load_config(args.config)
    args = merge_with_args(config, args)
    setup_logging(args.verbose)

    if args.find_html:
        if not args.docs_root:
            logging.error("Для --find-html укажите --docs-root")
            sys.exit(1)
        
        if not os.path.exists(args.docs_root):
            logging.error(f"Папка не найдена: {args.docs_root}")
            sys.exit(1)
        
        scan_html_files(args.docs_root)
        return

    if not args.qhp or not args.qhcp or not args.output:
        logging.error("Укажите --qhp, --qhcp и --output")
        logging.info("Используйте --help для справки")
        sys.exit(1)

    logging.info("=" * 60)
    logging.info("Qt Help Compiler Tool")
    logging.info("=" * 60)
    logging.info(f"Конфиг: {args.config}")
    logging.info(f".qhp: {args.qhp}")
    logging.info(f".qhcp: {args.qhcp}")
    logging.info(f"Выходной: {args.output}")
    logging.info(f"Internal: {'ДА' if args.internal else 'НЕТ'}")
    logging.info(f"Verbose: {'ВКЛ' if args.verbose else 'ВЫКЛ'}")

    if not validate_inputs(args):
        logging.error("Проверка входных данных не пройдена")
        sys.exit(1)

    try:
        logging.info("=" * 60)
        logging.info("ШАГ 1: Загрузка .qhp")
        preprocessor = QHPPreprocessor(args.qhp)
        if not preprocessor.load():
            logging.error("Не удалось загрузить .qhp")
            sys.exit(1)

        logging.info("ШАГ 2: Обработка internal")
        if not args.internal:
            removed = preprocessor.remove_internal_elements()
            logging.info(f"Удалено {removed} internal-элементов")
        else:
            internal = preprocessor.root.findall(".//*[@internal='yes']")
            logging.info(f"Сохранено {len(internal)} internal-элементов")

        logging.info("ШАГ 3: Обработка path")
        preprocessor.process_path_attributes(docs_root=args.docs_root)

        logging.info("ШАГ 4: Объединение .qhp")
        merger = QHPMerger(preprocessor)
        merged = merger.merge_all()
        logging.info(f"Объединено {merged} .qhp")

        logging.info("ШАГ 5: Сохранение временного .qhp")
        temp_qhp = preprocessor.save_temp()
        logging.info(f"Временный файл: {temp_qhp}")

        logging.info("=" * 60)
        logging.info("ШАГ 6: Запуск qhelpgenerator")
        qhelp_path = find_qhelpgenerator(args.qt_bin)
        wrapper = QHelpGeneratorWrapper(qhelp_path)

        success = wrapper.generate(
            qhp_path=temp_qhp,
            qhcp_path=args.qhcp,
            output_path=args.output,
            verbose=args.verbose
        )

        if success:
            logging.info("=" * 60)
            logging.info(f"Справка собрана: {args.output}")
            logging.info("=" * 60)
        else:
            logging.error("Ошибка при сборке")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()