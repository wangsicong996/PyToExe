from pathlib import Path

desktop = Path.home() / "Desktop"
main_folder = desktop / "ПопалсяЛОХ"
main_folder.mkdir(exist_ok=True)

for item in desktop.iterdir():
    if item == main_folder:
        continue

    # создаём папку с именем файла/папки
    new_folder = main_folder / item.stem  # item.stem для файлов без расширения
    new_folder.mkdir(exist_ok=True)

    # перемещаем объект в новую папку
    dest = new_folder / item.name
    item.rename(dest)

