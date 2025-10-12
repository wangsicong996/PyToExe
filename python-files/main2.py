import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# NOTA: Asegúrate de que todos tus scripts estén en el mismo directorio.

# Diccionario que mapea el nombre del botón al nombre del archivo de script
SCRIPTS = {
    "1. Gravitación": "gravitación.py",
    "2. Electricidad": "electrico.py",
    "3. Magnetismo": "magnetismo.py",
    "4. Óptica Física": "ópticaf.py",
    "5. Óptica Geométrica (Gráfico)": "ópticag.py",
    "6. Movimiento Armónico Simple": "mas.py",
    "7. Ondas Armónicas Unidimensionales": "oau.py",
    "8. Física Cuántica": "cuántica.py",
    "9. Física Nuclear": "nuclear.py",
    "10. Relatividad": "relatividad.py",
    "11. Sonido": "sonido.py",
}

def ejecutar_script(nombre_archivo):
    """
    Ejecuta el script de Python en una nueva ventana de terminal (consola) o directamente si es Tkinter.
    """
    if nombre_archivo in ["cuántica.py", "nuclear.py", "relatividad.py"]:
        # Para scripts Tkinter, importar y ejecutar main() directamente
        try:
            if nombre_archivo == "cuántica.py":
                import cuántica
                cuántica.main()
            elif nombre_archivo == "nuclear.py":
                import nuclear
                nuclear.main()
            elif nombre_archivo == "relatividad.py":
                import relatividad
                relatividad.main()
        except ImportError:
            messagebox.showerror("Error", f"No se pudo importar el módulo: {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al ejecutar el script: {e}")
    else:
        # Para scripts de consola, ejecutar en terminal
        ruta_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)

        try:
            if sys.platform.startswith('win'):
                # Forzar UTF-8 en la terminal y evitar cierre inmediato
                python_ejecutable = sys.executable
                comando = f'start cmd /k "chcp 65001 > nul && {python_ejecutable} \"{ruta_script}\" & pause"'
                subprocess.Popen(comando, shell=True)
            elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
                comando = ['gnome-terminal', '--', 'python3', ruta_script]
                subprocess.Popen(comando)
            else:
                messagebox.showerror("Error", "Sistema operativo no compatible con ejecución en terminal separada.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró el archivo: {nombre_archivo}. Asegúrate de que esté en la carpeta del ejecutable.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al ejecutar el script: {e}")


# --- Configuración de la Ventana Tkinter ---

root = tk.Tk()
root.title("PROYECTO PYTHON - Física")
root.update_idletasks()
ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
# Dejar un pequeño margen
root.geometry(f"{ancho_pantalla-80}x{alto_pantalla-80}+40+40")
root.resizable(False, False)

tk.Label(root, text="Selecciona el tema a calcular:", font=('Arial', 14, 'bold')).pack(pady=20)

# Frame para los botones en grid de 2 columnas
frame_botones = tk.Frame(root)
frame_botones.pack(pady=10)

# Crear un botón para cada script en grid
for i, (etiqueta, archivo) in enumerate(SCRIPTS.items()):
    row = i // 2
    col = i % 2
    # Usamos una función lambda para pasar el argumento al handler del botón
    boton = tk.Button(
        frame_botones,
        text=etiqueta, 
        command=lambda f=archivo: ejecutar_script(f),
        width=30,  # Más pequeño para caber en 2 columnas
        height=2,
        font=('Arial', 12),
        bg='#f0f0f0' # Color de fondo ligero
    )
    boton.grid(row=row, column=col, pady=8, padx=10)

# Botón de Salir
tk.Button(
    root, 
    text="Salir", 
    command=root.quit,
    width=50,  # Más largo
    height=2,
    font=('Arial', 14),
    bg='#ffcccc', # Color de fondo de advertencia
    fg='red'
).pack(pady=20)

root.mainloop()