import os
import shutil
import textwrap
import sys

def format_size(size_bytes):
    """Форматирует размер в удобочитаемый вид (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"

def add_dummy_data(input_file, target_size_mb):
    try:
        # Удаляем кавычки из пути, если они есть
        input_file = input_file.strip('"\'')
        
        # Проверяем существование файла
        if not os.path.exists(input_file):
            print("Ошибка: Файл не существует!")
            return False
        
        # Проверяем расширение файла
        valid_extensions = {
            # Изображения
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.heic', '.psd',
            # Видео
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.m4v', '.3gp',
            # Аудио
            '.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a',
            # Документы
            '.txt', '.doc', '.docx', '.pdf', '.odt', '.ods', '.odp', '.rtf', '.csv', '.xlsx', '.xls', '.ppt', '.pptx',
            # Архивы
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            # Код и данные
            '.py', '.java', '.cpp', '.c', '.cs', '.js', '.html', '.css', '.json', '.xml', '.sql', '.db', '.sqlite'
        }
        
        file_extension = os.path.splitext(input_file)[1].lower()
        if file_extension not in valid_extensions:
            print(f"Ошибка: Неподдерживаемый формат. Поддерживаемые форматы: {', '.join(sorted(valid_extensions))}")
            return False
        
        # Проверяем размер исходного файла
        original_size = os.path.getsize(input_file)
        target_size_bytes = int(target_size_mb * 1024 * 1024)  # Конвертируем МБ в байты
        
        if original_size >= target_size_bytes:
            print(f"Файл уже имеет размер {format_size(original_size)}, "
                  f"что больше или равно целевому ({format_size(target_size_bytes)}).")
            return False
        
        # Создаем временную копию файла
        output_file = f"modified_{os.path.basename(input_file)}"
        shutil.copyfile(input_file, output_file)
        
        # Открываем файл в режиме добавления
        with open(output_file, 'ab') as f:
            bytes_to_add = target_size_bytes - original_size
            chunk_size = 1024 * 1024  # 1 МБ
            while bytes_to_add > 0:
                chunk = int(min(chunk_size, bytes_to_add))
                f.write(os.urandom(chunk))  # Записываем случайные байты
                bytes_to_add -= chunk
        
        # Проверяем итоговый размер
        final_size = os.path.getsize(output_file)
        print(f"Файл успешно модифицирован. Новый размер: {format_size(final_size)}")
        print(f"Файл сохранен как: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return False

def print_wrapped(text):
    """Выводит текст с автопереносом строк в зависимости от ширины терминала."""
    terminal_width = shutil.get_terminal_size().columns
    wrapped_text = textwrap.wrap(text, width=terminal_width - 2)  # -2 для отступа
    for line in wrapped_text:
        print(line)

def main():
    # Выводим поддерживаемые форматы при запуске
    valid_extensions = {
        # Изображения
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.heic', '.psd',
        # Видео
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.m4v', '.3gp',
        # Аудио
        '.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a',
        # Документы
        '.txt', '.doc', '.docx', '.pdf', '.odt', '.ods', '.odp', '.rtf', '.csv', '.xlsx', '.xls', '.ppt', '.pptx',
        # Архивы
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
        # Код и данные
        '.py', '.java', '.cpp', '.c', '.cs', '.js', '.html', '.css', '.json', '.xml', '.sql', '.db', '.sqlite'
    }
    print_wrapped(f"Поддерживаемые форматы файлов: {', '.join(sorted(valid_extensions))}.")
    print("\n")

    while True:
        # Получаем путь к файлу
        input_file = input("Введите путь к файлу (или 'exit' для выхода): ").strip()
        if input_file.lower() == 'exit':
            print("Программа завершена.")
            sys.exit(0)
        
        # Получаем желаемый размер
        while True:
            try:
                target_size_mb_str = input("Введите желаемый размер файла (МБ): ").strip()
                target_size_mb = float(target_size_mb_str)
                if target_size_mb <= 0:
                    print("Ошибка: Размер должен быть больше 0!")
                    continue
                
                target_size_bytes = int(target_size_mb * 1024 * 1024)
                readable_size = format_size(target_size_bytes)
                print(f"Целевой размер: {readable_size}")
                
                confirm = input("Устраивает ли вас этот размер? (да/нет): ").strip().lower()
                if confirm in ['да', 'yes', 'y', 'д']:
                    break
                elif confirm in ['нет', 'no', 'n']:
                    close = input("Хотите ввести размер заново (1) или закрыть программу (2)? ").strip()
                    if close == '2':
                        print("Программа завершена.")
                        sys.exit(0)
                    # Если 1 или другое, продолжаем цикл ввода размера
                else:
                    print("Пожалуйста, ответьте 'да' или 'нет'.")
            except ValueError:
                print("Ошибка: Введите числовое значение для размера в МБ.")
        
        # Обрабатываем файл
        success = add_dummy_data(input_file, target_size_mb)
        
        # Предлагаем обработать следующий файл
        if success:
            next_file = input("Хотите обработать следующий файл? (да/нет): ").strip().lower()
            if next_file not in ['да', 'yes', 'y', 'д']:
                print("Программа завершена.")
                break
        else:
            # Если ошибка, все равно предлагаем следующий, но можно продолжить
            continue

if __name__ == "__main__":
    main()