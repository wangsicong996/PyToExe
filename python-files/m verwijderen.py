import os

# Map waarin de bestanden staan
folder = r'C:\12'  # <-- Pas dit pad aan

# Loop door alle bestanden in de map
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)

    if os.path.isfile(file_path):
        # Splits naam en extensie
        name, ext = os.path.splitext(filename)

        # Verwijder '_M' of '_m' van het einde van de naam
        if name.endswith('_M') or name.endswith('_m'):
            new_name = name[:-2] + ext  # Verwijder laatste 2 tekens
            new_path = os.path.join(folder, new_name)
            print(f"Naam wijzigen: {filename} → {new_name}")
            os.rename(file_path, new_path)

print("Klaar. Alle bestandsnamen zijn aangepast.")
input("Druk op Enter om te sluiten...")