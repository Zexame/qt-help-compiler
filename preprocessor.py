import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import logging
import shutil
import tempfile


class QHPPreprocessor:
    """Обработка .qhp файлов: загрузка, парсинг, модификация."""

    def __init__(self, qhp_path):
        self.qhp_path = qhp_path
        self.tree = None
        self.root = None
        self.namespace = ""

    def load(self):
        try:
            self.tree = ET.parse(self.qhp_path)
            self.root = self.tree.getroot()

            if self.root.tag.startswith('{'):
                self.namespace = self.root.tag.split('}')[0] + '}'

            logging.info(f"Загружен: {self.qhp_path}")
            logging.debug(f"Корневой элемент: {self.root.tag}")
            return True

        except ET.ParseError as e:
            logging.error(f"Ошибка парсинга XML: {e}")
            return False
        except FileNotFoundError:
            logging.error(f"Файл не найден: {self.qhp_path}")
            return False

    def save(self, output_path=None):
        if output_path is None:
            output_path = self.qhp_path

        try:
            xml_str = ET.tostring(self.root, encoding='unicode')
            dom = minidom.parseString(xml_str)
            pretty = dom.toprettyxml(indent="    ")
            pretty = '\n'.join([line for line in pretty.split('\n') if line.strip()])

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty)
            return True
        except Exception as e:
            logging.error(f"Ошибка сохранения: {e}")
            return False

    def remove_internal_elements(self):
        internal = self.root.findall(".//*[@internal='yes']")
        if not internal:
            logging.info("Internal-элементы не найдены")
            return 0

        logging.info(f"Найдено internal-элементов: {len(internal)}")
        removed = 0

        for elem in internal:
            parent = self._find_parent(elem)
            if parent is not None:
                parent.remove(elem)
                removed += 1
                logging.debug(f"Удален: {elem.tag} (title='{elem.get('title', 'N/A')}')")

        return removed

    def _find_parent(self, element):
        for parent in self.root.iter():
            if element in parent:
                return parent
        return None

    def process_path_attributes(self, docs_root=None):
        elements = self.root.findall(".//*[@path]")
        if not elements:
            logging.info("Атрибуты path не найдены")
            return 0

        logging.info(f"Найдено элементов с path: {len(elements)}")
        qhp_dir = os.path.dirname(os.path.abspath(self.qhp_path))

        copied = 0
        errors = []

        for elem in elements:
            try:
                ref = elem.get('ref', '')
                path_attr = elem.get('path', '')
                if not ref or not path_attr:
                    continue

                # исходный файл
                if os.path.isabs(path_attr):
                    src = path_attr
                else:
                    src = os.path.normpath(os.path.join(qhp_dir, path_attr))

                # целевой файл
                if os.path.isabs(ref):
                    dst = ref
                else:
                    dst = os.path.normpath(os.path.join(qhp_dir, ref))

                # создаём целевую папку
                dst_dir = os.path.dirname(dst)
                if dst_dir and not os.path.exists(dst_dir):
                    os.makedirs(dst_dir, exist_ok=True)
                    logging.debug(f"Создана папка: {dst_dir}")

                # проверяем существование исходного
                if not os.path.exists(src) and docs_root:
                    alt = os.path.normpath(os.path.join(docs_root, path_attr))
                    if os.path.exists(alt):
                        src = alt
                        logging.debug(f"Найден в docs_root: {src}")

                if not os.path.exists(src):
                    errors.append(f"Файл не найден: {path_attr}")
                    continue

                shutil.copy2(src, dst)
                copied += 1
                logging.debug(f"Скопирован: {os.path.basename(src)} -> {ref}")
                del elem.attrib['path']

            except Exception as e:
                errors.append(str(e))
                logging.error(f"Ошибка: {e}")

        if errors:
            logging.warning(f"Ошибок копирования: {len(errors)}")
            for err in errors:
                logging.warning(f"  {err}")

        logging.info(f"Скопировано файлов: {copied}")
        return copied

    def save_temp(self):
        temp_dir = tempfile.mkdtemp(prefix="qt_help_")
        temp_path = os.path.join(temp_dir, "temp_help.qhp")
        self.save(temp_path)
        logging.debug(f"Временный файл: {temp_path}")
        return temp_path

    def print_structure(self):
        def walk(elem, indent=0):
            prefix = "  " * indent
            attrs = " ".join(f'{k}="{v}"' for k, v in elem.attrib.items())
            print(f"{prefix}<{elem.tag} {attrs}>" if attrs else f"{prefix}<{elem.tag}>")
            for child in elem:
                walk(child, indent + 1)

        print("Структура документа:")
        walk(self.root)