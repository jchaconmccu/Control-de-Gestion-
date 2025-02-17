# src/__init__.py

# Importar módulos clave del proyecto para facilitar su uso
default_app_name = "Mi Aplicación Streamlit"

def print_welcome():
    print(f"Bienvenido a {default_app_name}!")

# Puedes importar aquí los módulos del proyecto para facilitar su acceso
def load_modules():
    from . import processing
    from . import visualization
    return processing, visualization
