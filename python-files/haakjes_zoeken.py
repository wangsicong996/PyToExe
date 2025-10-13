import os
import re
import shutil

# De map waarin je wilt zoeken
source_folder = r'C:\12'

# Map waar de bestanden naartoe moeten
destination_folder = r'C:\13'

# Zorg dat de bestemmingsmap bestaat
os.makedirs(destination_folder, exist_ok=True)

# Regex om te zoeken naar bestanden die haakjes bevatten
pattern = re.compile(r'[()]+')

# Loop door alle bestanden in de map
for file in os.listdir(source_folder):
    source_path = os.path.join(source_folder, file)
    if os.path.isfile(source_path) and pattern.search(file):
        destination_path = os.path.join(destination_folder, file)
        print(f"Verplaatsen: {source_path} -> {destination_path}")
        shutil.move(source_path, destination_path)

print("Alle bestanden met haakjes zijn verplaatst.")
input("Druk op Enter om het venster te sluiten...")