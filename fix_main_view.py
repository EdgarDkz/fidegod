import re

# Leer el archivo original
with open('views/main_view.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Reemplazar la firma del método __init__
pattern = r'def __init__\(self, parent\):'
replacement = 'def __init__(self, parent, theme_manager=None):'
modified_content = re.sub(pattern, replacement, content)

# Añadir el atributo theme_manager después de self.parent = parent
pattern = r'self\.parent = parent\n'
replacement = 'self.parent = parent\n        self.theme_manager = theme_manager\n'
modified_content = re.sub(pattern, replacement, modified_content)

# Añadir la lógica para usar los colores del theme_manager
pattern = r'# Paleta de colores base - Tema Pastel Suave \(Naranja\)'
replacement = '# Usar colores del theme_manager si está disponible\n        if theme_manager:\n            self.colors = theme_manager.get_color_palette()\n        else:\n            # Paleta de colores base - Tema Pastel Suave (Naranja)'
modified_content = re.sub(pattern, replacement, modified_content)

# Escribir el archivo modificado
with open('views/main_view.py', 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("Archivo main_view.py modificado correctamente.") 