# Sistema de Gestión de Inventario

Sistema de gestión de inventario con interfaz gráfica desarrollado en Python usando Tkinter.

## Características

- Gestión completa de inventario (CRUD)
- Interfaz gráfica moderna e intuitiva
- Búsqueda en tiempo real
- Filtros avanzados
- Exportación a Excel
- Gestión de imágenes de productos
- Sistema de alertas de stock
- Atajos de teclado

## Requisitos

- Python 3.8 o superior
- Pillow (PIL)
- tkcalendar
- pandas
- openpyxl

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Para iniciar la aplicación:
```bash
python main.py
```

### Atajos de Teclado

- `Ctrl + N`: Nuevo artículo
- `Ctrl + F`: Buscar
- `Ctrl + R`: Recargar datos
- `Ctrl + E`: Exportar a Excel
- `Delete`: Eliminar artículo seleccionado

### Funcionalidades Principales

1. **Gestión de Artículos**
   - Agregar nuevos artículos
   - Editar artículos existentes
   - Eliminar artículos
   - Gestionar imágenes de productos

2. **Búsqueda y Filtros**
   - Búsqueda en tiempo real
   - Filtros por categoría
   - Filtros por estado de stock
   - Filtros avanzados (fecha, ubicación, etc.)

3. **Exportación de Datos**
   - Exportar inventario a Excel
   - Reportes personalizados

4. **Control de Stock**
   - Alertas de stock bajo
   - Stock mínimo configurable
   - Estado visual del stock

## Estructura del Proyecto

```
├── main.py
├── requirements.txt
├── README.md
├── controllers/
│   ├── __init__.py
│   └── inventario_controller.py
├── models/
│   ├── __init__.py
│   └── db.py
└── views/
    ├── __init__.py
    ├── inventario_view.py
    └── Inventario_dialogs/
        ├── __init__.py
        ├── add_producto_dialog.py
        └── edit_producto_dialog.py
```

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 