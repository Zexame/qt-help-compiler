import os
import logging
from datetime import datetime


def scan_html_files(root_dir, output_dir="html_find_out"):
    root_dir = os.path.abspath(root_dir)
    root_name = os.path.basename(root_dir)
    
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"html_scan_{timestamp}.txt")
    
    html_files = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.html', '.htm')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
                
                if rel_path == '.':
                    full_ref = f"{root_name}.html"
                else:
                    full_ref = f"{root_name}/{rel_path}"
                
                html_files.append({
                    'full_path': full_path,
                    'rel_path': rel_path,
                    'ref_path': full_ref,
                    'name': os.path.splitext(file)[0]
                })
    
    html_files.sort(key=lambda x: x['ref_path'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("СКАНИРОВАНИЕ HTML-ФАЙЛОВ\n")
        f.write(f"Папка: {root_dir}\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Найдено: {len(html_files)}\n")
        f.write("=" * 80 + "\n\n")
        
        if not html_files:
            f.write("HTML-файлы не найдены\n")
            logging.info(f"HTML-файлы не найдены в: {root_dir}")
            return
        
        f.write("-" * 80 + "\n")
        f.write("1. СТРУКТУРА ДЛЯ <toc>\n")
        f.write("-" * 80 + "\n")
        f.write("# Скопируйте в секцию <toc>\n\n")
        
        for item in html_files:
            title = item['name'].replace('_', ' ').replace('-', ' ').title()
            f.write(f'<section title="{title}" ref="{item["ref_path"]}"/>\n')
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("2. СТРОКИ ДЛЯ <files>\n")
        f.write("-" * 80 + "\n")
        f.write("# Скопируйте в секцию <files>\n\n")
        
        for item in html_files:
            f.write(f'<file>{item["ref_path"]}</file>\n')
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("3. СТРОКИ ДЛЯ <keywords>\n")
        f.write("-" * 80 + "\n")
        f.write("# Скопируйте в секцию <keywords>\n\n")
        
        for item in html_files:
            keyword = item['name'].replace('_', ' ').replace('-', ' ').title()
            f.write(f'<keyword name="{keyword}" ref="{item["ref_path"]}"/>\n')
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("4. СТРОКИ С АТРИБУТОМ path\n")
        f.write("-" * 80 + "\n")
        f.write("# Если файлы лежат вне структуры проекта\n\n")
        
        for item in html_files:
            title = item['name'].replace('_', ' ').replace('-', ' ').title()
            path_display = item['full_path'].replace('\\', '/')
            f.write(f'<section title="{title}" ref="{item["ref_path"]}" path="{path_display}"/>\n')
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("5. СПИСОК ВСЕХ ФАЙЛОВ\n")
        f.write("-" * 80 + "\n")
        
        for i, item in enumerate(html_files, 1):
            f.write(f"  {i:3d}. {item['ref_path']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Всего: {len(html_files)} файлов\n")
        f.write("=" * 80 + "\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("ИНСТРУКЦИЯ\n")
        f.write("-" * 80 + "\n")
        f.write("1. Скопируйте строки в .qhp\n")
        f.write("2. Отредактируйте title при необходимости\n")
        f.write("3. Запустите сборку\n")
    
    print("\n" + "=" * 60)
    print(f"Найдено: {len(html_files)} HTML-файлов")
    print(f"Результат: {output_file}")
    print("=" * 60)