import os
import logging
import xml.etree.ElementTree as ET
from preprocessor import QHPPreprocessor


class QHPMerger:
    """Объединение нескольких .qhp файлов."""

    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.root = preprocessor.root
        self.qhp_dir = os.path.dirname(os.path.abspath(preprocessor.qhp_path))
        self.merged_count = 0

    def merge_all(self):
        sections = self.root.findall(".//section[@ref]")
        self.merged_count = 0

        for section in sections:
            ref = section.get('ref', '')
            if ref.endswith('.qhp'):
                logging.info(f"Ссылка на .qhp: {ref}")
                if self._merge_qhp(section, ref):
                    self.merged_count += 1

        return self.merged_count

    def _merge_qhp(self, parent_section, qhp_path):
        try:
            if os.path.isabs(qhp_path):
                full_path = qhp_path
            else:
                full_path = os.path.normpath(os.path.join(self.qhp_dir, qhp_path))

            logging.debug(f"Загрузка: {full_path}")

            if not os.path.exists(full_path):
                logging.warning(f".qhp не найден: {full_path}")
                return False

            child = QHPPreprocessor(full_path)
            if not child.load():
                logging.warning(f"Не удалось загрузить: {full_path}")
                return False

            child_root = child.root
            child_dir = os.path.dirname(full_path)

            # toc
            child_toc = child_root.find(".//toc")
            if child_toc is not None:
                for sec in child_toc.findall("section"):
                    new_sec = self._clone_with_updated_paths(sec, child_dir, self.qhp_dir)
                    parent_section.append(new_sec)
                    logging.debug(f"  Добавлена секция: {new_sec.get('title', 'N/A')}")

            # keywords
            child_keywords = child_root.find(".//keywords")
            if child_keywords is not None:
                parent_keywords = self.root.find(".//keywords")
                if parent_keywords is None:
                    filter_sec = self.root.find(".//filterSection")
                    if filter_sec is None:
                        filter_sec = ET.Element("filterSection")
                        self.root.append(filter_sec)
                    parent_keywords = ET.Element("keywords")
                    filter_sec.append(parent_keywords)

                for kw in child_keywords.findall("keyword"):
                    new_kw = ET.Element(kw.tag, kw.attrib)
                    new_kw.text = kw.text
                    ref = new_kw.get('ref', '')
                    if ref:
                        new_kw.set('ref', self._update_ref_path(ref, child_dir, self.qhp_dir))
                    parent_keywords.append(new_kw)
                    logging.debug(f"  Добавлено ключевое слово: {new_kw.get('name', 'N/A')}")

            # files
            child_files = child_root.find(".//files")
            if child_files is not None:
                parent_files = self.root.find(".//files")
                if parent_files is None:
                    filter_sec = self.root.find(".//filterSection")
                    if filter_sec is None:
                        filter_sec = ET.Element("filterSection")
                        self.root.append(filter_sec)
                    parent_files = ET.Element("files")
                    filter_sec.append(parent_files)

                for f in child_files.findall("file"):
                    new_f = ET.Element(f.tag)
                    new_f.text = f.text
                    parent_files.append(new_f)
                    logging.debug(f"  Добавлен файл: {new_f.text}")

            # удаляем секцию-ссылку
            parent = self.preprocessor._find_parent(parent_section)
            if parent is not None:
                parent.remove(parent_section)
                logging.debug(f"Удалена секция-ссылка: {parent_section.get('title', 'N/A')}")

            return True

        except Exception as e:
            logging.error(f"Ошибка при объединении {qhp_path}: {e}")
            return False

    def _clone_with_updated_paths(self, source, source_dir, target_dir):
        new_section = ET.Element(source.tag, source.attrib)
        new_section.text = source.text

        ref = new_section.get('ref', '')
        if ref:
            new_section.set('ref', self._update_ref_path(ref, source_dir, target_dir))

        for child in source:
            new_child = self._clone_with_updated_paths(child, source_dir, target_dir)
            new_section.append(new_child)

        return new_section

    def _update_ref_path(self, ref_path, source_dir, target_dir):
        if os.path.isabs(ref_path):
            return ref_path

        full = os.path.normpath(os.path.join(source_dir, ref_path))
        if not os.path.exists(full):
            logging.debug(f"Файл не найден, путь не обновлён: {ref_path}")
            return ref_path

        try:
            rel = os.path.relpath(full, target_dir).replace('\\', '/')
            logging.debug(f"Путь обновлён: {ref_path} -> {rel}")
            return rel
        except ValueError:
            logging.debug(f"Разные диски, путь не обновлён: {ref_path}")
            return ref_path