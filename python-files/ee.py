import os
import random
import shutil
from pathlib import Path

def add_dummy_data(input_file, target_size_mb):
    """
    Добавляет искусственный вес к файлу до указанного размера в МБ.
    
    Args:
        input_file (str): Путь к исходному файлу.
        target_size_mb (float): Желаемый размер файла в мегабайтах.
    """
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(input_file):
            print(f"Файл {input_file} не существует!")
            return
        
        # Получаем размер исходного файла в байтах
        original_size = os.path.getsize(input_file)
        target_size_bytes = int(target_size_mb * 1024 * 1024)  # Конвертируем МБ в байты и приводим к int
        
        if original_size >= target_size_bytes:
            print(f"Файл уже имеет размер {original_size / (1024 * 1024):.2f} МБ, что больше или равно целевому ({target_size_mb} МБ).")
            return
        
        # Создаем временную копию файла
        file_extension = os.path.splitext(input_file)[1]
        output_file = f"modified_{os.path.basename(input_file)}"
        shutil.copyfile(input_file, output_file)
        
        # Открываем файл в режиме добавления
        with open(output_file, 'ab') as f:
            # Вычисляем, сколько байтов нужно добавить
            bytes_to_add = target_size_bytes - original_size
            
            # Добавляем случайные данные
            chunk_size = 1024 * 1024  # 1 МБ
            while bytes_to_add > 0:
                chunk = int(min(chunk_size, bytes_to_add))  # Приводим к int
                f.write(os.urandom(chunk))  # Записываем случайные байты
                bytes_to_add -= chunk
            
        # Проверяем итоговый размер
        final_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"Файл успешно модифицирован. Новый размер: {final_size:.2f} МБ")
        print(f"Файл сохранен как: {output_file}")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        input("Нажмите Enter, чтобы закрыть...")

def main():
    print("Программа для увеличения размера файлов")
    print("Поддерживаемые форматы: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .mp3, .wav, .ogg, .txt, .doc, .docx, .pdf, .xlsx, .pptx, .zip, .rar, .7z")
    
    # Запрашиваем у пользователя путь к файлу
    input_file = input("Введите путь к файлу: ").strip()
    
    # Проверяем, является ли файл допустимым
    valid_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',  # Изображения
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',  # Видео
        '.mp3', '.wav', '.ogg',  # Аудио
        '.txt', '.doc', '.docx', '.pdf', '.xlsx', '.pptx',  # Документы
        '.zip', '.rar', '.7z'  # Архивы
    }
    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension not in valid_extensions:
        print(f"Неподдерживаемый формат файла. Поддерживаемые форматы: {', '.join(valid_extensions)}")
        input("Нажмите Enter, чтобы закрыть...")
        return
    
    # Запрашиваем целевой размер
    while True:
        try:
            target_size_mb = float(input("Введите желаемый размер файла в МБ: "))
            if target_size_mb <= 0:
                print("Размер должен быть больше 0!")
                continue
            break
        except ValueError:
            print("Пожалуйста, введите числовое значение для размера в МБ.")
    
    # Вызываем функцию для добавления веса
    add_dummy_data(input_file, target_size_mb)
    input("Нажмите Enter, чтобы закрыть...")

if __name__ == "__main__":
    main()