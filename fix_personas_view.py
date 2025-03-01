import re

def fix_file():
    original_file = 'views/personas_view.py'
    
    # Leer el contenido del archivo
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y eliminar la segunda definición de _get_relative_font_size
    pattern = r'tk\.Canvas\.create_rounded_rectangle = create_rounded_rectangle\s+def _get_relative_font_size\(self, base_size\):[^_]+def _adjust_button_size'
    replacement = 'tk.Canvas.create_rounded_rectangle = create_rounded_rectangle\n\n    def _adjust_button_size'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Guardar el contenido modificado
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('Archivo editado correctamente.')

if __name__ == "__main__":
    fix_file() 