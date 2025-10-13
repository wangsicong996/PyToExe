import os
import shutil
import textwrap
import sys
import curses  # Для обработки клавиш, включая Escape

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
        
        # Проверяем, является ли путь пустым
        if not input_file:
            print("Ошибка: Путь к файлу не может быть пустым!")
            return False
        
        # Проверяем существование файла
        if not os.path.exists(input_file):
            print("Ошибка: Файл не существует!")
            return False
        
        # Проверяем, является ли это файлом (не директорией)
        if not os.path.isfile(input_file):
            print("Ошибка: Указанный путь ведет к директории, а не к файлу!")
            return False
        
        # Проверяем права на чтение файла
        if not os.access(input_file, os.R_OK):
            print("Ошибка: Нет прав на чтение файла!")
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
        
        # Создаем имя выходного файла
        output_file = f"modified_{os.path.basename(input_file)}"
        
        # Проверяем, существует ли выходной файл
        if os.path.exists(output_file):
            overwrite = get_yes_no_input(f"Файл '{output_file}' уже существует. Перезаписать?")
            if not overwrite:
                print("Операция отменена.")
                return False
        
        # Пытаемся скопировать файл
        try:
            shutil.copyfile(input_file, output_file)
        except PermissionError:
            print("Ошибка: Нет прав на запись в директорию!")
            return False
        except shutil.Error as e:
            print(f"Ошибка при копировании файла: {str(e)}")
            return False
        except Exception as e:
            print(f"Неизвестная ошибка при копировании: {str(e)}")
            return False
        
        # Проверяем права на запись в выходной файл
        if not os.access(output_file, os.W_OK):
            print("Ошибка: Нет прав на запись в выходной файл!")
            os.remove(output_file)  # Удаляем копию, если создана
            return False
        
        # Открываем файл в режиме добавления
        try:
            with open(output_file, 'ab') as f:
                bytes_to_add = target_size_bytes - original_size
                chunk_size = 1024 * 1024  # 1 МБ
                while bytes_to_add > 0:
                    chunk = int(min(chunk_size, bytes_to_add))
                    f.write(os.urandom(chunk))  # Записываем случайные байты
                    bytes_to_add -= chunk
        except IOError as e:
            print(f"Ошибка ввода/вывода при записи: {str(e)} (возможно, диск заполнен)")
            os.remove(output_file)  # Удаляем неудавшуюся копию
            return False
        except Exception as e:
            print(f"Неизвестная ошибка при записи: {str(e)}")
            os.remove(output_file)
            return False
        
        # Проверяем итоговый размер
        final_size = os.path.getsize(output_file)
        if final_size < target_size_bytes:
            print("Предупреждение: Итоговый размер меньше ожидаемого (возможно, проблемы с диском).")
            return False
        
        print(f"Файл успешно модифицирован. Новый размер: {format_size(final_size)}")
        print(f"Файл сохранен как: {output_file}")
        
        return True
        
    except ValueError as e:
        print(f"Ошибка значения: {str(e)} (возможно, некорректный размер)")
        return False
    except OSError as e:
        print(f"Системная ошибка: {str(e)}")
        return False
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {str(e)}")
        return False

def print_wrapped(text):
    """Выводит текст с автопереносом строк в зависимости от ширины терминала."""
    try:
        terminal_width = shutil.get_terminal_size().columns
    except Exception:
        terminal_width = 80  # Значение по умолчанию, если не удалось получить ширину
    wrapped_text = textwrap.wrap(text, width=terminal_width - 2)  # -2 для отступа
    for line in wrapped_text:
        print(line)

def get_input(prompt):
    """Функция для ввода с обработкой Escape с использованием curses."""
    def curses_input(stdscr):
        curses.echo()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()
        input_str = ''
        while True:
            key = stdscr.getch()
            if key == 27:  # Escape key
                raise KeyboardInterrupt("Escape pressed")
            elif key == 10 or key == 13:  # Enter
                break
            elif key == 127 or key == 8:  # Backspace
                if input_str:
                    input_str = input_str[:-1]
                    stdscr.delch(0, len(prompt) + len(input_str))
                    stdscr.refresh()
            else:
                input_str += chr(key)
                stdscr.addch(chr(key))
                stdscr.refresh()
        return input_str.strip()
    
    try:
        return curses.wrapper(curses_input)
    except KeyboardInterrupt:
        print("\nПрограмма завершена по нажатию Escape.")
        sys.exit(0)

def get_yes_no_input(prompt):
    """Получает да/нет с объяснением вариантов: 1=да, 2=нет, Enter=да."""
    print(f"{prompt} (1 - да, 2 - нет, Enter - да по умолчанию)")
    while True:
        try:
            response = get_input("")  # Пустой промпт, так как уже напечатан
            if response == '' or response.lower() in ['1', 'да', 'yes', 'y', 'д']:
                return True
            elif response.lower() in ['2', 'нет', 'no', 'n']:
                return False
            else:
                print("Пожалуйста, ответьте 1 (да), 2 (нет) или Enter (да).")
        except KeyboardInterrupt:
            print("\nПрограмма завершена по нажатию Escape.")
            sys.exit(0)

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
    print("Нажмите Escape в любой момент для выхода из программы.")

    while True:
        try:
            # Получаем путь к файлу
            input_file = get_input("Введите путь к файлу (или 'exit' для выхода): ")
            if input_file.lower() == 'exit':
                print("Программа завершена.")
                sys.exit(0)
            
            if not input_file:
                print("Ошибка: Путь к файлу не может быть пустым!")
                continue
            
            # Получаем желаемый размер
            while True:
                try:
                    target_size_mb_str = get_input("Введите желаемый размер файла (МБ): ")
                    if not target_size_mb_str:
                        print("Ошибка: Размер не может быть пустым!")
                        continue
                    target_size_mb = float(target_size_mb_str)
                    if target_size_mb <= 0:
                        print("Ошибка: Размер должен быть больше 0!")
                        continue
                    
                    if target_size_mb > 1024 * 1024:  # Например, лимит 1 ТБ для безопасности
                        print("Ошибка: Запрошенный размер слишком велик (максимум 1 ТБ)!")
                        continue
                    
                    target_size_bytes = int(target_size_mb * 1024 * 1024)
                    readable_size = format_size(target_size_bytes)
                    print(f"Целевой размер: {readable_size}")
                    
                    confirmed = get_yes_no_input("Устраивает ли вас этот размер?")
                    
                    if confirmed:
                        break
                    else:
                        close_choice = get_input("Хотите ввести размер заново (1) или закрыть программу (2)? ")
                        if close_choice == '2':
                            print("Программа завершена.")
                            sys.exit(0)
                        # Если 1 или другое, продолжаем цикл ввода размера
                except ValueError:
                    print("Ошибка: Введите числовое значение для размера в МБ.")
            
            # Обрабатываем файл
            success = add_dummy_data(input_file, target_size_mb)
            
            # Предлагаем обработать следующий файл
            if success:
                next_file = get_yes_no_input("Хотите обработать следующий файл?")
                if not next_file:
                    print("Программа завершена.")
                    sys.exit(0)
            else:
                # Если ошибка, предлагаем попробовать снова
                continue
        except KeyboardInterrupt:
            print("\nОперация прервана пользователем. Программа завершена.")
            sys.exit(0)
        except Exception as e:
            print(f"Неизвестная ошибка в основном цикле: {str(e)}")
            continue

if __name__ == "__main__":
    main()