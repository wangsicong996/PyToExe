import os
import random
import shutil

def add_dummy_data(input_file, target_size_mb):
    try:
        # Удаляем кавычки из пути, если они есть
        input_file = input_file.strip('"\'')
        
        # Проверяем существование файла
        if not os.path.exists(input_file):
            print("Ошибка: Файл не существует!")
            return
        
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
            print(f"Ошибка: Неподдерживаемый формат. Поддерживаемые форматы: {', '.join(valid_extensions)}")
            return
        
        # Проверяем размер исходного файла
        original_size = os.path.getsize(input_file)
        target_size_bytes = int(target_size_mb * 1024 * 1024)  # Конвертируем МБ в байты
        
        if original_size >= target_size_bytes:
            print(f"Файл уже имеет размер {original_size / (1024 * 1024):.2f} МБ, "
                  f"что больше или равно целевому ({target_size_mb} МБ).")
            return
        
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
        final_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"Файл успешно модифицирован. Новый размер: {final_size:.2f} МБ")
        print(f"Файл сохранен как: {output_file}")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

def main():
    # Получаем путь к файлу
    input_file = input("Введите путь к файлу: ").strip()
    
    # Получаем желаемый размер
    while True:
        try:
            target_size_mb = float(input("Введите желаемый размер файла (МБ): ").strip())
            if target_size_mb <= 0:
                print("Ошибка: Размер должен быть больше 0!")
                continue
            break
        except ValueError:
            print("Ошибка: Введите числовое значение для размера в МБ.")
    
    # Обрабатываем файл
    add_dummy_data(input_file, target_size_mb)

if __name__ == "__main__":
    main()