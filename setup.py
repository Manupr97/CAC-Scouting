import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=== Configuración del entorno para CAC Scouting ===")
    
    # Verificar Python
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    
    if sys.version_info < (3, 7):
        print("Error: Se requiere Python 3.7 o superior")
        sys.exit(1)
    
    # Crear estructura de directorios
    dirs = ["data", "reports", "reports/photos", "assets", "db"]
    
    for d in dirs:
        path = Path(d)
        if not path.exists():
            path.mkdir()
            print(f"Directorio creado: {d}")
        else:
            print(f"Directorio existente: {d}")
    
    # Comprobar y crear un logo predeterminado si no existe
    logo_path = Path("assets/Escudo CAC.png")
    if not logo_path.exists():
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear un logo básico
            img = Image.new('RGB', (200, 200), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Intentar agregar texto
            try:
                font = ImageFont.truetype("arial.ttf", 50)
            except IOError:
                font = ImageFont.load_default()
            
            draw.text((50, 70), "CAC", fill=(255, 255, 255), font=font)
            img.save(logo_path)
            print(f"Logo predeterminado creado en {logo_path}")
        except Exception as e:
            print(f"No se pudo crear un logo predeterminado: {e}")
            print("Por favor, proporciona un logo en assets/logo.png")
    
    # Instalar dependencias
    dependencies = [
        "streamlit",
        "pandas",
        "numpy",
        "matplotlib",
        "plotly",
        "openpyxl",  # Para leer archivos Excel
        "xlrd",      # Para archivos Excel más antiguos
        "reportlab", # Para generar PDFs
        "pillow",    # Para manipulación de imágenes
        "beautifulsoup4",  # Para scraping web
        "requests",  # Para peticiones HTTP
    ]
    
    print("\nInstalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        for dep in dependencies:
            print(f"Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print("Todas las dependencias se instalaron correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar dependencias: {e}")
        sys.exit(1)
    
    # Verificar la importación de streamlit
    try:
        import streamlit
        print(f"Streamlit instalado correctamente (versión {streamlit.__version__})")
    except ImportError:
        print("Error: No se pudo importar streamlit. Por favor, instálalo manualmente con 'pip install streamlit'")
        sys.exit(1)
    
    # Crear un archivo .streamlit/config.toml para personalización
    streamlit_config_dir = Path.home() / ".streamlit"
    streamlit_config_dir.mkdir(exist_ok=True)
    
    config_file = streamlit_config_dir / "config.toml"
    with open(config_file, "w") as f:
        f.write("""
[theme]
primaryColor = "#FFFFFF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1E1E1E"
textColor = "#FFFFFF"
font = "sans serif"
        """)
    
    print(f"Archivo de configuración de Streamlit creado en {config_file}")
    
    # Instrucciones finales
    print("\n=== Configuración completada ===")
    print("Para ejecutar la aplicación, usa el siguiente comando:")
    print(f"{sys.executable} -m streamlit run New_Web_Scouting.py")
    print("\nRecuerda:")
    print("1. Coloca los archivos Excel de datos en la carpeta 'data'")
    print("2. El usuario administrador predeterminado es 'admin' con contraseña 'admin123'")
    print("3. Personaliza el logo colocando una imagen en 'assets/logo.png'")

if __name__ == "__main__":
    main()