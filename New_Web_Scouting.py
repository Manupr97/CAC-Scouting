import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64
import requests
import json
import datetime
import time
import os
import io
from bs4 import BeautifulSoup
import hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
import sqlite3
from PIL import Image as PILImage
import matplotlib as mpl
mpl.use('Agg')  # Usar el backend Agg para evitar problemas con Streamlit
from mplsoccer import Radar, grid
import matplotlib.font_manager as fm
from io import BytesIO

# Configuración de página
st.set_page_config(
    page_icon="cac-scouting\assets\Escudo CAC.png", 
    page_title="CAC Scouting", 
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Directorio de la aplicación
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
REPORTS_DIR = APP_DIR / "reports"
ASSETS_DIR = APP_DIR / "assets"
DB_DIR = APP_DIR / "db"
FONTS_DIR = ASSETS_DIR / "fonts"

# Crear directorios si no existen
for dir_path in [DATA_DIR, REPORTS_DIR, ASSETS_DIR, DB_DIR, FONTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Archivo de base de datos SQLite
DB_FILE = DB_DIR / "scouting.db"

# Función para inicializar la base de datos
def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de informes de scouting
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scouting_reports (
        id INTEGER PRIMARY KEY,
        report_date TEXT NOT NULL,
        match_date TEXT NOT NULL,
        local_team TEXT NOT NULL,
        visitor_team TEXT NOT NULL,
        result TEXT NOT NULL,
        player_name TEXT NOT NULL,
        player_club TEXT NOT NULL,
        position TEXT NOT NULL,
        overall_rating INTEGER NOT NULL,
        is_starter INTEGER NOT NULL,
        minutes_played INTEGER NOT NULL,
        technical_aspects TEXT NOT NULL,
        tactical_aspects TEXT NOT NULL,
        physical_aspects TEXT NOT NULL,
        psychological_aspects TEXT NOT NULL,
        observations TEXT,
        photo_path TEXT,
        created_by INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    # Tabla de noticias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        source TEXT NOT NULL,
        url TEXT,
        published_date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Verificar si el usuario admin ya existe
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # Crear un usuario admin por defecto
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", admin_password, "admin")
        )
    
    conn.commit()
    conn.close()

# Inicializar la base de datos al inicio
initialize_database()

# Función para convertir imagen a base64
def get_base64_from_file(file_path):
    """Convierte una imagen local a código base64 para insertar en HTML"""
    try:
        path = Path(file_path)
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return encoded
    except:
        return None

# Función para la pantalla de carga personalizada
def add_splash_screen():
    logo_path = ASSETS_DIR / "Escudo CAC.png"
    
    # Si no existe el logo, usar un placeholder o crear uno básico
    if not logo_path.exists():
        # Crear un logo básico si no existe
        img = PILImage.new('RGB', (200, 200), color=(0, 0, 0))
        img.save(logo_path)
    
    logo_base64 = get_base64_from_file(logo_path)
    
    splash_css = """
    <style>
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    @keyframes fadeOut {
        0% { opacity: 1; }
        100% { opacity: 0; }
    }
    
    .splash-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #000000;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeOut 1s ease-in-out 2.5s forwards;
        pointer-events: none;
    }
    
    .splash-logo {
        width: 150px;
        margin-bottom: 20px;
        animation: fadeIn 1.5s ease-in-out;
    }
    
    .splash-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
        animation: fadeIn 1.5s ease-in-out 0.5s both;
    }
    
    .splash-subtitle {
        color: #cccccc;
        font-size: 1.2rem;
        text-align: center;
        max-width: 80%;
        animation: fadeIn 1.5s ease-in-out 1s both;
    }
    </style>
    """
    
    splash_html = f"""
    <div class="splash-screen" id="splashScreen">
        <img src="data:image/png;base64,{logo_base64}" class="splash-logo">
        <div class="splash-title">CAC Scouting</div>
        <div class="splash-subtitle">#SoñarEsGratis</div>
    </div>
    
    <script>
        setTimeout(function() {{
            const splash = document.getElementById('splashScreen');
            if (splash) {{
                splash.style.opacity = 0;
                setTimeout(function() {{
                    if (splash && splash.parentNode) {{
                        splash.parentNode.removeChild(splash);
                    }}
                }}, 1000);
            }}
        }}, 2500);
    </script>
    """
    
    st.markdown(splash_css, unsafe_allow_html=True)
    st.markdown(splash_html, unsafe_allow_html=True)

# Estilos CSS personalizados para la aplicación
def load_css():
    st.markdown("""
    <style>
    /* Estilos globales */
    body {
        color: #F0F2F6;
        background-color: #0E1117;
    }
    
    /* Barra lateral */
    .css-1d391kg {
        background-color: #000000;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
    }
    
    /* Cards personalizados */
    .custom-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Botones primarios */
    .stButton>button {
        background-color: #FFFFFF;
        color: #000000;
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #CCCCCC;
        color: #000000;
    }
    
    /* Selectbox y otros widgets */
    .stSelectbox>div>div {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    /* Contenedor para las noticias */
    .news-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .news-item {
        background-color: #1E1E1E;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #FFFFFF;
        transition: transform 0.3s;
    }
    
    .news-item:hover {
        transform: translateY(-5px);
    }
    
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .news-source {
        font-size: 0.8rem;
        color: #AAAAAA;
    }
    
    .news-date {
        font-size: 0.8rem;
        color: #AAAAAA;
        text-align: right;
    }
    
    /* Estilos para el login */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #1E1E1E;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabla de datos */
    .dataframe {
        width: 100%;
        border-collapse: collapse;
    }
    
    .dataframe th {
        background-color: #000000;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    
    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #444444;
    }
    
    .dataframe tr:hover {
        background-color: #2E2E2E;
    }
    
    /* Paginación */
    .pagination {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    
    .page-link {
        color: white;
        background-color: #000000;
        padding: 8px 16px;
        margin: 0 4px;
        border-radius: 4px;
        text-decoration: none;
    }
    
    .page-link:hover {
        background-color: #333333;
    }
    
    /* Tarjetas de jugadores */
    .player-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
    }
    
    .player-card:hover {
        transform: translateY(-5px);
    }
    
    .player-header {
        background-color: #000000;
        color: white;
        padding: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .player-body {
        padding: 15px;
    }
    
    .stat-label {
        color: #AAAAAA;
        font-size: 0.9rem;
    }
    
    .stat-value {
        color: white;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    /* Formularios */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea {
        background-color: #2E2E2E;
        color: white;
        border: 1px solid #444444;
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus {
        border-color: white;
    }
    
    /* Para dispositivos móviles */
    @media (max-width: 768px) {
        .player-card {
            margin-bottom: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Función para verificar la autenticación
def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_id = None
    
    return st.session_state.authenticated

# Función para mostrar el login
def show_login():
    st.markdown("<h1 style='text-align: center;'>CAC Scouting</h1>", unsafe_allow_html=True)
    
    # Logo centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = ASSETS_DIR / "Escudo CAC.png"
        if logo_path.exists():
            # obtenemos la imagen en base64 (tienes ya la función get_base64_from_file)
            logo_b64 = get_base64_from_file(logo_path)
            # la insertamos centrada con HTML
            st.markdown(
                f"""
                <div style="text-align:center; margin-bottom: 1rem;">
                    <img src="data:image/png;base64,{logo_b64}" width="200" />
                </div>
                """,
                unsafe_allow_html=True
            )
    

    # Contenedor del formulario de login
    st.subheader("Iniciar Sesión")
    
    username = st.text_input("Usuario", key="login_username")
    password = st.text_input("Contraseña", type="password", key="login_password")
    
    if st.button("Acceder"):
        if not username or not password:
            st.error("Por favor, completa todos los campos")
        else:
            hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, role FROM users WHERE username = ? AND password = ?",
                (username, hashed_pwd)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, role = result
                st.session_state.authenticated = True
                st.session_state.user_role = role
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Función para obtener las noticias
def get_news_from_web(source_url, limit=5):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(source_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        
        # Adaptado para BeSoccer - ajustar según la estructura real del sitio
        articles = soup.select('.content-new')[:limit]
        
        for article in articles:
            title_elem = article.select_one('.title-new')
            link_elem = article.select_one('a')
            date_elem = article.select_one('.date-new')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                url = link_elem['href'] if 'href' in link_elem.attrs else ''
                if not url.startswith('http'):
                    url = f"https://es.besoccer.com{url}"
                
                published_date = date_elem.text.strip() if date_elem else datetime.datetime.now().strftime("%d/%m/%Y")
                
                news_items.append({
                    'title': title,
                    'content': '',  # No extraemos el contenido completo
                    'source': 'BeSoccer',
                    'url': url,
                    'published_date': published_date
                })
        
        return news_items
    except Exception as e:
        st.warning(f"Error al obtener noticias: {e}")
        return []

# Función para guardar noticias en la base de datos
def save_news_to_db(news_items):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    for item in news_items:
        # Verificar si la noticia ya existe
        cursor.execute(
            "SELECT id FROM news WHERE title = ? AND source = ?",
            (item['title'], item['source'])
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO news (title, content, source, url, published_date) VALUES (?, ?, ?, ?, ?)",
                (item['title'], item['content'], item['source'], item['url'], item['published_date'])
            )
    
    conn.commit()
    conn.close()

# Función para obtener noticias de la base de datos
def get_news_from_db(limit=10):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, title, content, source, url, published_date FROM news ORDER BY published_date DESC LIMIT ?",
        (limit,)
    )
    news = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return news

# Función mejorada para cargar datos y evitar duplicados
@st.cache_data(ttl=3600)
def load_all_player_data():
    """
    Carga todos los datos de jugadores de los archivos Excel en la carpeta data,
    eliminando duplicados.
    
    Returns:
        DataFrame: DataFrame combinado con todos los datos de jugadores
    """
    # Intentar cargar archivos de Excel
    try:
        excel_files = list(DATA_DIR.glob("*.xlsx"))
        if not excel_files:
            st.warning("No se encontraron archivos Excel en la carpeta 'data'")
            return pd.DataFrame()
            
        st.info(f"Archivos Excel encontrados: {[f.name for f in excel_files]}")
        
        dfs = []
        for file in excel_files:
            try:
                df = pd.read_excel(file)
                # Verificar que el DataFrame tiene las columnas necesarias
                if 'jugador' not in df.columns or 'equipo' not in df.columns:
                    st.warning(f"El archivo {file.name} no tiene la estructura esperada (faltan columnas)")
                    continue
                
                # Agregar columna con el nombre del archivo como fuente
                df['data_source'] = file.name
                
                # Mostrar información del DataFrame
                st.info(f"Archivo {file.name}: {df.shape[0]} jugadores, {df.shape[1]} columnas")
                
                dfs.append(df)
            except Exception as e:
                st.error(f"Error al cargar el archivo {file.name}: {e}")
        
        # Combinar todos los dataframes
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            # Eliminar duplicados basados en jugador y equipo
            original_count = combined_df.shape[0]
            combined_df = combined_df.drop_duplicates(subset=['jugador', 'equipo'], keep='first')
            
            # Informar sobre duplicados eliminados
            duplicates_removed = original_count - combined_df.shape[0]
            if duplicates_removed > 0:
                st.info(f"Se eliminaron {duplicates_removed} registros duplicados")
            
            return combined_df
        
        # Si no hay archivos válidos, devolver un dataframe vacío
        st.warning("No se pudieron cargar datos válidos de ningún archivo")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error general al cargar datos: {e}")
        return pd.DataFrame()

# Función para cargar un archivo específico
@st.cache_data(ttl=3600)
def load_specific_data(file_path):
    """
    Carga un archivo Excel específico.
    
    Args:
        file_path (Path): Ruta al archivo Excel
    
    Returns:
        DataFrame: DataFrame con los datos del archivo
    """
    try:
        if not file_path.exists():
            st.error(f"El archivo {file_path} no existe")
            return pd.DataFrame()
            
        df = pd.read_excel(file_path)
        
        # Verificar que el DataFrame tiene las columnas necesarias
        if 'jugador' not in df.columns or 'equipo' not in df.columns:
            st.warning(f"El archivo {file_path.name} no tiene la estructura esperada (faltan columnas)")
        
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo {file_path.name}: {e}")
        return pd.DataFrame()

# Función para detectar y eliminar duplicados
def remove_duplicates(df):
    """
    Elimina registros duplicados del DataFrame basándose en jugador y equipo.
    
    Args:
        df (DataFrame): DataFrame original
    
    Returns:
        DataFrame: DataFrame sin duplicados
    """
    if df.empty:
        return df
    
    # Verificar si existen las columnas necesarias
    if 'jugador' not in df.columns or 'equipo' not in df.columns:
        st.warning("El DataFrame no tiene las columnas 'jugador' y 'equipo' necesarias para eliminar duplicados")
        return df
    
    # Contar registros originales
    original_count = df.shape[0]
    
    # Eliminar duplicados
    df_cleaned = df.drop_duplicates(subset=['jugador', 'equipo'], keep='first')
    
    # Informar sobre duplicados eliminados
    duplicates_removed = original_count - df_cleaned.shape[0]
    if duplicates_removed > 0:
        st.info(f"Se eliminaron {duplicates_removed} registros duplicados")
    
    return df_cleaned

# Función para preparar los datos para el radar chart
def prepare_radar_data(df, player_name, metrics):
    """
    Prepara los datos para el radar chart, normalizando los valores.
    
    Args:
        df (DataFrame): DataFrame con los datos de los jugadores
        player_name (str): Nombre del jugador
        metrics (list): Lista de métricas a visualizar
    
    Returns:
        tuple: (valores normalizados, métricas disponibles)
    """
    # Verificar que existe el jugador
    if player_name not in df['jugador'].values:
        st.error(f"Jugador '{player_name}' no encontrado en los datos")
        return None, None
    
    # Filtrar jugador seleccionado
    player_data = df[df['jugador'] == player_name]
    
    # Verificar que existen las métricas
    available_metrics = [m for m in metrics if m in df.columns]
    if not available_metrics:
        st.error("Ninguna de las métricas seleccionadas está disponible en los datos")
        return None, None
    
    # Normalizar valores para el radar chart
    normalized_values = []
    raw_values = []
    
    for metric in available_metrics:
        try:
            value = player_data[metric].iloc[0]
            raw_values.append(value)
            
            # Normalizar solo si es un valor válido
            if pd.notna(value) and pd.api.types.is_numeric_dtype(df[metric]):
                min_val = df[metric].min()
                max_val = df[metric].max()
                
                if max_val > min_val:
                    norm_value = (value - min_val) / (max_val - min_val)
                    normalized_values.append(norm_value)
                else:
                    normalized_values.append(0.5)  # Valor por defecto
            else:
                normalized_values.append(0)  # Valor por defecto para no numéricos
        except Exception as e:
            st.error(f"Error al preparar la métrica {metric}: {e}")
            normalized_values.append(0)
    
    return normalized_values, available_metrics, raw_values

# Función para generar informe PDF
def generate_report_pdf(report_data):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        report_elements = []
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  # Centrado
            spaceAfter=20
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        
        normal_style = styles['Normal']
        
        # Título del informe
        report_elements.append(Paragraph(f"INFORME DE SCOUTING - {report_data['player_name']}", title_style))
        report_elements.append(Spacer(1, 0.25*inch))
        
        # Datos del partido
        match_data = [
            ["Fecha del partido:", report_data['match_date']],
            ["Equipo local:", report_data['local_team']],
            ["Equipo visitante:", report_data['visitor_team']],
            ["Resultado:", report_data['result']]
        ]
        match_table = Table(match_data, colWidths=[2.5*inch, 3*inch])
        match_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.black),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        report_elements.append(match_table)
        report_elements.append(Spacer(1, 0.25*inch))
        
        # Datos del jugador
        player_data = [
            ["Jugador:", report_data['player_name']],
            ["Club:", report_data['player_club']],
            ["Posición:", report_data['position']],
            ["Valoración general:", f"{report_data['overall_rating']}/10"],
            ["Titular:", "Sí" if report_data['is_starter'] else "No"],
            ["Minutos jugados:", f"{report_data['minutes_played']}"]
        ]
        player_table = Table(player_data, colWidths=[2.5*inch, 3*inch])
        player_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.black),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        report_elements.append(player_table)
        report_elements.append(Spacer(1, 0.25*inch))
        
        # Secciones de análisis
        sections = [
            ("ASPECTOS TÉCNICOS", report_data['technical_aspects']),
            ("ASPECTOS TÁCTICOS", report_data['tactical_aspects']),
            ("ASPECTOS FÍSICOS", report_data['physical_aspects']),
            ("ASPECTOS PSICOLÓGICOS", report_data['psychological_aspects']),
            ("OBSERVACIONES", report_data['observations'])
        ]
        
        for title, content in sections:
            report_elements.append(Paragraph(title, subtitle_style))
            report_elements.append(Paragraph(content, normal_style))
            report_elements.append(Spacer(1, 0.25*inch))
        
        # Agregar foto si existe
        if report_data['photo_path'] and os.path.exists(report_data['photo_path']):
            try:
                img = Image(report_data['photo_path'], width=3*inch, height=4*inch)
                report_elements.append(img)
            except:
                report_elements.append(Paragraph("Error al cargar la imagen del jugador", normal_style))
        
        # Agregar fecha de generación del informe
        report_elements.append(Spacer(1, 0.5*inch))
        report_elements.append(Paragraph(f"Informe generado el {report_data['report_date']}", normal_style))
        
        # Construir el PDF
        doc.build(report_elements)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
        return None

# Función para guardar un informe en la base de datos
def save_report_to_db(report_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO scouting_reports (
        report_date, match_date, local_team, visitor_team, result,
        player_name, player_club, position, overall_rating, is_starter,
        minutes_played, technical_aspects, tactical_aspects, physical_aspects,
        psychological_aspects, observations, photo_path, created_by
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report_data['report_date'],
        report_data['match_date'],
        report_data['local_team'],
        report_data['visitor_team'],
        report_data['result'],
        report_data['player_name'],
        report_data['player_club'],
        report_data['position'],
        report_data['overall_rating'],
        1 if report_data['is_starter'] else 0,
        report_data['minutes_played'],
        report_data['technical_aspects'],
        report_data['tactical_aspects'],
        report_data['physical_aspects'],
        report_data['psychological_aspects'],
        report_data['observations'],
        report_data['photo_path'],
        report_data['created_by']
    ))
    
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return report_id

# Función para obtener informes de la base de datos
def get_reports_from_db(limit=50, offset=0, player_filter=None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
    SELECT r.*, u.username as scout_name
    FROM scouting_reports r
    JOIN users u ON r.created_by = u.id
    '''
    
    params = []
    
    if player_filter:
        query += " WHERE r.player_name LIKE ?"
        params.append(f"%{player_filter}%")
    
    query += " ORDER BY r.match_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    reports = [dict(row) for row in cursor.fetchall()]
    
    # Contar el total de informes
    count_query = "SELECT COUNT(*) FROM scouting_reports"
    count_params = []
    
    if player_filter:
        count_query += " WHERE player_name LIKE ?"
        count_params.append(f"%{player_filter}%")
    
    cursor.execute(count_query, count_params)
    total_reports = cursor.fetchone()[0]
    
    conn.close()
    
    return reports, total_reports

# Función para obtener un informe específico
def get_report_by_id(report_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT r.*, u.username as scout_name
    FROM scouting_reports r
    JOIN users u ON r.created_by = u.id
    WHERE r.id = ?
    ''', (report_id,))
    
    report = cursor.fetchone()
    conn.close()
    
    return dict(report) if report else None

# Función para generar tabla comparativa
def generate_comparison_table(player_data, metrics, player_names):
    if not player_names or not metrics:
        st.error("Selecciona al menos un jugador y una métrica para comparar")
        return None
    
    # Filtrar jugadores
    filtered_data = player_data[player_data['jugador'].isin(player_names)]
    
    if filtered_data.empty:
        st.error("Ninguno de los jugadores seleccionados se encuentra en los datos")
        return None
    
    # Filtrar métricas disponibles
    available_metrics = ['jugador'] + [m for m in metrics if m in filtered_data.columns]
    
    if len(available_metrics) <= 1:
        st.error("Ninguna de las métricas seleccionadas está disponible en los datos")
        return None
    
    # Crear dataframe de comparación
    comparison_df = filtered_data[available_metrics].copy()
    
    # Formatear números para mejor visualización
    for col in comparison_df.columns:
        if col != 'jugador' and pd.api.types.is_numeric_dtype(comparison_df[col]):
            # Determinar si es porcentaje o valor normal
            if 'pct' in col.lower() or '%' in col:
                comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
            elif any(x in col.lower() for x in ['/90', 'ratio', 'xa', 'xg']):
                comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
            else:
                comparison_df[col] = comparison_df[col].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "-")
    
    return comparison_df

# Función para generar ranking de jugadores según métricas
def generate_player_ranking(player_data, metric, min_minutes=0, position=None, limit=20):
    if metric not in player_data.columns:
        st.error(f"La métrica '{metric}' no está disponible en los datos")
        return None
    
    # Filtrar por minutos jugados
    filtered_data = player_data[player_data['min'] >= min_minutes].copy()
    
    # Filtrar por posición si se especifica
    if position and position != "Todas":
        filtered_data = filtered_data[filtered_data['pos'] == position]
    
    if filtered_data.empty:
        st.error("No hay datos que cumplan con los filtros especificados")
        return None
    
    # Ordenar por la métrica seleccionada (descendente)
    ranked_data = filtered_data.sort_values(by=metric, ascending=False).head(limit)
    
    # Seleccionar columnas para mostrar
    display_columns = ['jugador', 'equipo', 'pos', 'min']
    if metric not in display_columns:
        display_columns.append(metric)
    
    ranked_data = ranked_data[display_columns]
    
    return ranked_data

# Función para crear un usuario
def create_user(username, password, role):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "El nombre de usuario ya existe"
        
        # Crear el nuevo usuario
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_pwd, role)
        )
        
        conn.commit()
        conn.close()
        return True, "Usuario creado correctamente"
    
    except Exception as e:
        return False, f"Error al crear usuario: {e}"

# Función para obtener la lista de usuarios
def get_users():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY username")
    users = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return users

# Función para eliminar un usuario
def delete_user(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True, "Usuario eliminado correctamente"
    
    except Exception as e:
        return False, f"Error al eliminar usuario: {e}"

# Función para cambiar contraseña
def change_password(user_id, new_password):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        hashed_pwd = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hashed_pwd, user_id)
        )
        
        conn.commit()
        conn.close()
        return True, "Contraseña actualizada correctamente"
    
    except Exception as e:
        return False, f"Error al cambiar contraseña: {e}"
    
# Función para mostrar sección de Home
def show_home():
    st.header("🏠 Inicio")
    
    # Contenedor para las noticias
    with st.container():
        st.subheader("Últimas noticias")
        
        # Actualizar noticias desde fuentes web
        if st.button("🔄 Actualizar noticias"):
            with st.spinner("Obteniendo las últimas noticias..."):
                news_sources = [
                    "https://es.besoccer.com/noticias/competicion/tercera_division_rfef",
                    "https://es.besoccer.com/noticias/competicion/segunda_division_rfef",
                    "https://es.besoccer.com/noticias/competicion/primera_division_rfef"
                ]
                
                all_news = []
                for source in news_sources:
                    news = get_news_from_web(source, limit=3)
                    all_news.extend(news)
                
                if all_news:
                    save_news_to_db(all_news)
                    st.success(f"Se han actualizado {len(all_news)} noticias")
                else:
                    st.warning("No se encontraron nuevas noticias")
        
        # Mostrar noticias desde la base de datos
        news_items = get_news_from_db(limit=10)
        
        if not news_items:
            st.info("No hay noticias disponibles. Haz clic en 'Actualizar noticias' para obtener las últimas.")
        else:
            st.markdown("<div class='news-container'>", unsafe_allow_html=True)
            
            for news in news_items:
                st.markdown(f"""
                <div class='news-item'>
                    <div class='news-title'>{news['title']}</div>
                    <div class='news-source'>Fuente: {news['source']}</div>
                    <div class='news-date'>{news['published_date']}</div>
                    <a href='{news['url']}' target='_blank'>Leer más</a>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Estadísticas del sistema
    with st.container():
        st.subheader("Estadísticas del sistema")
        
        # Obtener estadísticas
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM scouting_reports")
        reports_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scouting_reports WHERE date(created_at) = date('now')")
        reports_today = cursor.fetchone()[0]
        
        conn.close()
        
        # Mostrar estadísticas en columnas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='custom-card'>
                <h3 style='margin-bottom:10px;'>📋 Informes totales</h3>
                <p style='font-size:30px;font-weight:bold;'>{reports_count}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='custom-card'>
                <h3 style='margin-bottom:10px;'>👥 Usuarios activos</h3>
                <p style='font-size:30px;font-weight:bold;'>{users_count}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='custom-card'>
                <h3 style='margin-bottom:10px;'>📊 Informes hoy</h3>
                <p style='font-size:30px;font-weight:bold;'>{reports_today}</p>
            </div>
            """, unsafe_allow_html=True)

# Función para mostrar sección de Base de Datos
def show_database():
    st.header("📊 Base de Datos")
    st.write("Aquí puedes filtrar y visualizar datos de jugadores de las diferentes competiciones.")
    
    # Selector de competición
    comp_options = {
        "Todas": "wyscout_1ra_2da_RFEF_limpio.xlsx",
        "1ra RFEF": "wyscout_1ra_RFEF_limpio.xlsx",
        "2da RFEF": "wyscout_2da_RFEF_limpio.xlsx"
    }
    
    comp = st.selectbox("Competición", list(comp_options.keys()))
    season = st.selectbox("Temporada", ["24/25"])
    
    # Cargar datos según competición seleccionada
    data_file = comp_options[comp]
    data_path = DATA_DIR / data_file
    
    if not data_path.exists():
        st.error(f"Archivo no encontrado: {data_file}. Por favor, asegúrate de que existe en la carpeta 'data'.")
        # Intentar cargar cualquier archivo disponible
        excel_files = list(DATA_DIR.glob("*.xlsx"))
        if excel_files:
            data_path = excel_files[0]
            st.warning(f"Se cargará un archivo alternativo: {data_path.name}")
        else:
            st.stop()
    
    # Cargar el dataframe
    @st.cache_data(ttl=3600)
    def load_specific_data(file_path):
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return pd.DataFrame()
    
    df = load_specific_data(data_path)
    
    if df.empty:
        st.warning("No hay datos disponibles. Por favor, comprueba los archivos en la carpeta 'data'.")
        st.stop()
    
    # Definir los grupos de columnas
    column_groups = {
        "GENERAL": [
            "jugador", "equipo", "pos", "pos_secun", "pj", "min", 
            "anio_nac", "edad", "pais_nat", "pasap", "valor_tm",
            "fin_contrato", "prestamo", "alt_cm", "peso_kg", "pie"
        ],
        "FASE DEFENSIVA": [
            "acc_def/90", "duelos_def/90", "duelos_def_w_pct",
            "duelos_aer/90", "duelos_aer_w_pct", "entradas/90",
            "posesion_tras_entrada", "tiros_int/90",
            "interc/90", "posesion_tras_interc",
            "faltas/90", "TA", "TA/90", "TR", "TR/90", "duelos/90", "duelos_w_pct"
        ],
        "FASE OFENSIVA": [
            "goles", "goles/90", "goles_exc_pen", "goles_exc_pen/90",
            "goles_cabeza", "goles_cabeza/90", "remates", "remates/90", 
            "remates_port_pct", "xg", "xg/90", "goles_conv_pct", "desmarq/90",
            "desmarq_pct", "duelos_atq/90", "duelos_atq_w_pct",
            "toques_area_pen/90", "carreras_prog/90", "acel/90",
            "regates/90", "regates_pct", "centros/90",
            "centros_prec_pct", "centros_izq/90", "centros_izq_pct",
            "centros_der/90", "centros_der_pct",
            "centros_area_peq/90", "centros_ult_terc/90", "acc_atq/90", 
            "atq_prof/90", "faltas_rec/90"
        ],
        "ORGANIZACIÓN": [
            "asis", "asis/90", "xa", "xa/90", "pases/90", "pases_pct", 
            "pases_adel/90", "pases_adel_pct", "pases_atras/90", "pases_atras_pct",
            "pases_lat/90", "pases_lat_pct", "long_media_pases_m", 
            "long_media_pases_larg_m", "pases_rec/90", "pases_cor_med/90", 
            "pases_cor_med_pct", "pases_larg/90", "pases_larg_pct",
            "pases_prog/90", "pases_prog_pct", "pases_larg_rec/90"
        ],
        "PASES CLAVES": [
            "pases_ult_terc/90", "pases_ult_terc_pct",
            "jugadas_claves/90", "asis_disparo/90",
            "2da_asis/90", "3ra_asis/90", "pases_area_pen/90",
            "pases_area_peq_pct", "pases_prof/90", "pases_prof_pct" 
        ],
        "PORTERO": [
            "goles_recibidos", "goles_rec/90",
            "remates_en_contra", "remates_contra/90",
            "port_imbat/90", "paradas_pct",
            "xg_contra", "xg_contra/90",
            "goles_evitados", "goles_evit/90",
            "pases_rec_arq/90", "salidas/90",
            "duelos_aer_portero/90"
        ],
        "BALÓN PARADO": [
            "tiros_libres/90", "tiros_libres_direct/90",
            "tiros_libre_direc_pct", "corners/90",
            "penaltis_a_favor", "penaltis_conv_pct"
        ]
    }
    
    # Inicializar session_state si no existe
    if '_col_sel' not in st.session_state:
        st.session_state._col_sel = column_groups["GENERAL"][:10].copy()
    
    if 'temp_sel' not in st.session_state:
        st.session_state.temp_sel = st.session_state._col_sel.copy()
    
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    if 'open_cols' not in st.session_state:
        st.session_state.open_cols = False
    
    if 'active_group' not in st.session_state:
        st.session_state.active_group = "GENERAL"
    
    if 'open_filters' not in st.session_state:
        st.session_state.open_filters = False
    
    if 'active_filters' not in st.session_state:
        st.session_state.active_filters = []
    
    if 'filter_values' not in st.session_state:
        st.session_state.filter_values = {}
    
    if 'temp_active_filters' not in st.session_state:
        st.session_state.temp_active_filters = []
    
    # Definir rows_per_page solo aquí, para evitar duplicidad
    if 'rows_per_page_db' not in st.session_state:
        st.session_state.rows_per_page_db = 50
    
    # Funciones de callback
    def apply_columns_callback():
        st.session_state._col_sel = st.session_state.temp_sel.copy()

    def close_columns_callback():
        st.session_state.open_cols = False

    def apply_filters_callback():
        # No necesita hacer nada, ya que los valores ya están en session_state
        pass
    
    def close_filters_callback():
        st.session_state.open_filters = False

    def clear_filters_callback():
        st.session_state.active_filters = []
        st.session_state.filter_values = {}

    def go_prev():
        if st.session_state.page > 1:
            st.session_state.page -= 1

    def go_next(total):
        rpp = st.session_state.rows_per_page_db
        if st.session_state.page * rpp < total:
            st.session_state.page += 1
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def generate_filter_types(df, column_groups):
        """
        Genera dinámicamente los tipos de filtros basados en las columnas del DataFrame
        y la estructura de grupos de columnas existente, con detección automática de formato.
        """
        filter_types = {}
        
        # Para cada grupo en column_groups
        for group_name, columns in column_groups.items():
            filter_types[group_name] = {}
            
            # Solo incluir columnas que existan en el DataFrame
            valid_columns = [col for col in columns if col in df.columns]
            
            for col in valid_columns:
                # Determinar el tipo de filtro basado en el tipo de datos
                if pd.api.types.is_numeric_dtype(df[col].dtype):
                    # Para columnas numéricas
                    min_val = float(df[col].min()) if not pd.isna(df[col].min()) else 0
                    max_val = float(df[col].max()) if not pd.isna(df[col].max()) else 100
                    
                    # Determinar automáticamente formato y step según nombre y valores
                    column_format, step = determine_format_and_step(col, df[col])
                    
                    # Si es necesario redondear los valores límite según el formato
                    if column_format == "%d":  # Si es entero
                        min_val = int(min_val)
                        max_val = int(max_val)
                    
                    filter_types[group_name][col] = {
                        "type": "range", 
                        "min": min_val, 
                        "max": max_val,
                        "step": step,
                        "format": column_format
                    }
                
                elif pd.api.types.is_string_dtype(df[col].dtype) or pd.api.types.is_object_dtype(df[col].dtype):
                    # Para columnas de texto
                    unique_values = df[col].dropna().unique()
                    
                    # Si hay pocos valores únicos, usar multiselect
                    if len(unique_values) <= 50:  # umbral arbitrario
                        filter_types[group_name][col] = {
                            "type": "multiselect",
                            "options": sorted(unique_values.tolist())
                        }
                    else:
                        # Para texto con muchos valores únicos, usar búsqueda de texto
                        filter_types[group_name][col] = {"type": "text"}
                
                elif pd.api.types.is_bool_dtype(df[col].dtype):
                    # Para columnas booleanas
                    filter_types[group_name][col] = {"type": "toggle"}
                
                else:
                    # Predeterminado para otros tipos
                    filter_types[group_name][col] = {"type": "text"}
        
        # Personalizar algunos filtros específicos que necesiten ajustes especiales
        special_cases = {
            "jugador": {"type": "text"},
            "equipo": {"type": "multiselect", "options": sorted(df["equipo"].dropna().unique().tolist()) if "equipo" in df.columns else []},
            "pos": {"type": "multiselect", "options": sorted(df["pos"].dropna().unique().tolist()) if "pos" in df.columns else []},
            "pie": {"type": "multiselect", "options": sorted(df["pie"].dropna().unique().tolist()) if "pie" in df.columns else []}
        }
        
        # Aplicar casos especiales
        for group_name, filters in filter_types.items():
            for col_name in filters:
                if col_name in special_cases:
                    filters[col_name] = special_cases[col_name]
        
        return filter_types

    def determine_format_and_step(column_name, series):
        """
        Determina automáticamente el formato y step más adecuado para una columna.
        
        Args:
            column_name: Nombre de la columna
            series: Series de pandas con los datos
        
        Returns:
            tuple: (formato, step)
        """
        # Convertir el nombre de columna a minúsculas para comparación
        col_lower = column_name.lower()
        
        # Patrones para identificar columnas enteras
        integer_patterns = [
            'min', 'pj', 'gol', 'asis', 'ta', 'tr', 'remat', 'edad', 'alt', 'peso',
            'interc', 'entrada', 'pase', 'corner', 'centro', 'duelo', 'falta', 'tiro',
            'año', 'anio', 'salida', 'parada', 'toque'
        ]
        
        # Patrones para columnas con decimales precisos
        precise_decimal_patterns = ['/90', 'xa', 'xg', 'ratio', 'prom', 'media']
        
        # Patrones para porcentajes
        percentage_patterns = ['pct', '%', 'porc', 'conv']
        
        # Analizar también los datos reales
        has_decimals = False
        non_integer_values = False
        
        # Verificar si la serie contiene valores decimales
        if not series.empty:
            sample = series.dropna().head(100)  # Tomar una muestra para análisis
            has_decimals = any(x != int(x) for x in sample if pd.notna(x))
            if has_decimals:
                # Verificar si los decimales son significativos (no solo .0)
                non_integer_values = any(abs(x - round(x)) > 0.01 for x in sample if pd.notna(x))
        
        # Decisión basada en nombre de columna y datos reales
        if any(pattern in col_lower for pattern in integer_patterns) and not non_integer_values:
            return "%d", 1  # Formato entero, incremento 1
        
        elif any(pattern in col_lower for pattern in percentage_patterns):
            # Determinar si son porcentajes enteros o con decimales
            if non_integer_values:
                return "%.1f", 0.1  # Porcentajes con un decimal
            else:
                return "%d", 1  # Porcentajes enteros
                
        elif any(pattern in col_lower for pattern in precise_decimal_patterns) or non_integer_values:
            return "%.2f", 0.01  # Decimales precisos
            
        else:
            # Por defecto para valores numéricos
            if has_decimals:
                return "%.1f", 0.1  # Un decimal por defecto
            else:
                return "%d", 1  # Entero por defecto
    
    # Layout de dos columnas: filtros a la izquierda, contenido a la derecha
    col_filtros, col_main = st.columns([1, 4])
    
    # — columna izquierda: Filtros —
    with col_filtros:
        st.subheader("Filtros")
        
        # Generar los filtros dinámicamente
        filter_types = generate_filter_types(df, column_groups)
        
        # Botón para abrir el panel de selección de filtros
        def open_filter_panel():
            st.session_state.open_filters = True
            st.session_state.temp_active_filters = st.session_state.active_filters.copy()

        st.button("Filtros Avanzados", on_click=open_filter_panel, key="btn_open_filters")

        # Mostrar los filtros activos como "cards" separados
        if st.session_state.active_filters:
            st.markdown("### Filtros aplicados")
            
            # Variables para rastrear si algún filtro ha cambiado
            filter_modified = False
            temp_filter_values = {}
            
            # Crear una copia de los valores actuales para comparar cambios
            for fname in st.session_state.active_filters:
                if fname in st.session_state.filter_values:
                    temp_filter_values[fname] = st.session_state.filter_values[fname]
            
            # Contenedor para todos los filtros
            with st.container():
                for fname in st.session_state.active_filters:
                    f_info = None
                    for grp in filter_types.values():
                        if fname in grp:
                            f_info = grp[fname]
                            break
                    if f_info is None:
                        continue

                    ftype = f_info["type"]

                    # Cada filtro en su propio contenedor
                    with st.container():
                        st.markdown(f"**{fname}**")

                        # Rango numérico
                        if ftype == "range":
                            # Inicializar los valores del filtro si no existen
                            if fname not in temp_filter_values:
                                temp_filter_values[fname] = [f_info["min"], f_info["max"]]
                            
                            # Obtener los valores actuales
                            lo_def, hi_def = temp_filter_values[fname]
                            
                            # Crear controles para los valores min y max
                            cols = st.columns(2)
                            with cols[0]:
                                lo = st.number_input(
                                    "Min",
                                    min_value=f_info["min"],
                                    max_value=f_info["max"],
                                    value=lo_def,
                                    step=f_info.get("step", 1),
                                    format=f_info.get("format", "%d"),
                                    key=f"temp_range_{fname}_min"
                                )
                            with cols[1]:
                                hi = st.number_input(
                                    "Max",
                                    min_value=f_info["min"],
                                    max_value=f_info["max"],
                                    value=hi_def,
                                    step=f_info.get("step", 1),
                                    format=f_info.get("format", "%d"),
                                    key=f"temp_range_{fname}_max"
                                )
                            
                            # Guardar en valores temporales
                            new_value = [lo, hi]
                            if new_value != st.session_state.filter_values.get(fname, []):
                                filter_modified = True
                            temp_filter_values[fname] = new_value

                        elif ftype == "multiselect":
                            # Inicializar si no existe
                            if fname not in temp_filter_values:
                                temp_filter_values[fname] = []
                            
                            # Obtener valores actuales
                            current_values = temp_filter_values[fname]
                            
                            # Crear multiselect
                            new_sel = st.multiselect(
                                f"Seleccionar {fname}",
                                options=f_info["options"],
                                default=current_values,
                                key=f"temp_filter_{fname}"
                            )
                            
                            # Guardar en valores temporales
                            if new_sel != st.session_state.filter_values.get(fname, []):
                                filter_modified = True
                            temp_filter_values[fname] = new_sel

                        elif ftype == "text":
                            # Inicializar si no existe
                            if fname not in temp_filter_values:
                                temp_filter_values[fname] = ""
                            
                            # Obtener valor actual
                            current_text = temp_filter_values[fname]
                            
                            # Crear input de texto
                            new_txt = st.text_input(
                                f"Buscar en {fname}",
                                value=current_text,
                                key=f"temp_filter_{fname}"
                            )
                            
                            # Guardar en valores temporales
                            if new_txt != st.session_state.filter_values.get(fname, ""):
                                filter_modified = True
                            temp_filter_values[fname] = new_txt

                        elif ftype == "toggle":
                            # Inicializar si no existe
                            if fname not in temp_filter_values:
                                temp_filter_values[fname] = False
                            
                            # Obtener valor actual
                            current_toggle = temp_filter_values[fname]
                            
                            # Crear checkbox
                            new_tog = st.checkbox(
                                f"Activar {fname}",
                                value=current_toggle,
                                key=f"temp_filter_{fname}"
                            )
                            
                            # Guardar en valores temporales
                            if new_tog != st.session_state.filter_values.get(fname, False):
                                filter_modified = True
                            temp_filter_values[fname] = new_tog
            
            # Guardar valores temporales en el estado de la sesión para recuperarlos
            st.session_state.temp_filter_values = temp_filter_values
            
            # Botones para aplicar o limpiar filtros
            col1, col2 = st.columns(2)
            
            # Función para aplicar cambios en los filtros
            def apply_filter_changes():
                st.session_state.filter_values.update(st.session_state.temp_filter_values)
            
            with col1:
                st.button("Aplicar cambios", 
                        key="apply_filter_changes",
                        on_click=apply_filter_changes,
                        disabled=not filter_modified)  # Deshabilitar si no hay cambios
            
            with col2:
                st.button("Limpiar filtros", 
                        key="clear_filters_ui",
                        on_click=clear_filters_callback)
    
    # — Columna derecha: Columnas, tabla y paginación —
    with col_main:
        #  1) Botón que abre el expander y clona selección actual en temp_sel
        def open_panel():
            st.session_state.open_cols = True
            st.session_state.temp_sel = st.session_state._col_sel.copy()

        def apply_filter_selection():
            st.session_state.active_filters = st.session_state.temp_active_filters.copy()
            
            # Inicializar valores para nuevos filtros
            for fname in st.session_state.active_filters:
                # Buscar información del filtro
                for group, filters in filter_types.items():
                    if fname in filters:
                        f_info = filters[fname]
                        # Si es un filtro de rango y no tiene valores, inicializar
                        if f_info["type"] == "range" and fname not in st.session_state.filter_values:
                            st.session_state.filter_values[fname] = [f_info["min"], f_info["max"]]
                        # Si es multiselect y no tiene valores, inicializar como lista vacía
                        elif f_info["type"] == "multiselect" and fname not in st.session_state.filter_values:
                            st.session_state.filter_values[fname] = []
                        # Si es texto y no tiene valor, inicializar como cadena vacía
                        elif f_info["type"] == "text" and fname not in st.session_state.filter_values:
                            st.session_state.filter_values[fname] = ""
                        # Si es toggle y no tiene valor, inicializar como False
                        elif f_info["type"] == "toggle" and fname not in st.session_state.filter_values:
                            st.session_state.filter_values[fname] = False
                        break
            
            # Cerrar el panel de filtros sin forzar recarga completa
            st.session_state.open_filters = False
            
        st.button("Columnas", on_click=open_panel, key="btn_open_cols")

        panel = st.empty()
        if st.session_state.open_cols:
            with panel.container():
                st.markdown("### Selección de columnas")
                # ── "Seleccionar todo" fuera de formulario:
                if st.button("✅ Seleccionar todo", key="sel_all"):
                    st.session_state.temp_sel = df.columns.tolist()

                st.markdown("---")

                # ── Pestañas + checkboxes (igual que antes) ──
                tabs = st.tabs(list(column_groups.keys()))
                for tab, (grupo, cols) in zip(tabs, column_groups.items()):
                    with tab:
                        for i in range(0, len(cols), 3):
                            row = st.columns(3)
                            for j, colname in enumerate(cols[i : i + 3]):
                                if j < len(row): 
                                    checked = colname in st.session_state.temp_sel
                                    new = row[j].checkbox(
                                        colname,
                                        value=checked,
                                        key=f"tmp_{colname}"
                                    )
                                    if new and colname not in st.session_state.temp_sel:
                                        st.session_state.temp_sel.append(colname)
                                    if not new and colname in st.session_state.temp_sel:
                                        st.session_state.temp_sel.remove(colname)

                st.markdown("---")

                # ── 3) Botones independientes de Aplicar y Cerrar ──
                c1, c2 = st.columns(2)
                c1.button("Aplicar", key="apply_cols", on_click=apply_columns_callback)
                c2.button("Cerrar", key="close_cols", on_click=close_columns_callback)

                # Al cerrar, limpiamos el placeholder para que desaparezca de inmediato
                if not st.session_state.open_cols:
                    panel.empty()

        # Panel flotante para selección de filtros
        filter_panel = st.empty()
        if st.session_state.open_filters:
            with filter_panel.container():
                st.markdown("### Selección de filtros avanzados")
                
                # Botón "Seleccionar todos" para los filtros
                if st.button("✅ Seleccionar todos", key="sel_all_filters"):
                    st.session_state.temp_active_filters = []
                    for category, filters in filter_types.items():
                        for filter_name in filters:
                            st.session_state.temp_active_filters.append(filter_name)
                
                st.markdown("---")
                
                # Pestañas para las categorías de filtros
                filter_tabs = st.tabs(list(filter_types.keys()))
                
                for tab, (category, filters) in zip(filter_tabs, filter_types.items()):
                    with tab:
                        # Organizar los filtros en filas de 3
                        filters_list = list(filters.keys())
                        for i in range(0, len(filters_list), 3):
                            row = st.columns(3)
                            for j, filter_name in enumerate(filters_list[i : i + 3]):
                                if j < len(row):
                                    active = filter_name in st.session_state.temp_active_filters
                                    new = row[j].checkbox(
                                        filter_name,
                                        value=active,
                                        key=f"select_filter_{filter_name}"
                                    )
                                    if new and filter_name not in st.session_state.temp_active_filters:
                                        st.session_state.temp_active_filters.append(filter_name)
                                    if not new and filter_name in st.session_state.temp_active_filters:
                                        st.session_state.temp_active_filters.remove(filter_name)
                
                st.markdown("---")
                
                # Botones de acción
                col1, col2 = st.columns(2)
                col1.button("Confirmar selección", key="confirm_filter_selection", on_click=apply_filter_selection)
                col2.button("Cerrar", key="close_filters", on_click=close_filters_callback)
                    
                # Al cerrar, limpiamos el placeholder
                if not st.session_state.open_filters:
                    filter_panel.empty()

        # Aplicar filtros antes de mostrar el DataFrame
        df_filtered = df.copy()
        
        if st.session_state.active_filters:
            for filter_name in st.session_state.active_filters:
                if filter_name not in st.session_state.filter_values:
                    continue
                    
                filter_value = st.session_state.filter_values[filter_name]
                
                for category, filters in filter_types.items():
                    if filter_name in filters:
                        filter_info = filters[filter_name]
                        
                        if filter_name in df_filtered.columns:
                            if filter_info["type"] == "text" and filter_value:
                                # Búsqueda de texto con case insensitive
                                df_filtered = df_filtered[df_filtered[filter_name].astype(str).str.contains(
                                    filter_value, case=False, na=False)]
                            
                            elif filter_info["type"] == "range":
                                lo, hi = filter_value  # Ya tenemos los valores en session_state
                                df_filtered = df_filtered[(df_filtered[filter_name] >= lo) & 
                                                        (df_filtered[filter_name] <= hi)]
                            
                            elif filter_info["type"] == "multiselect" and filter_value:
                                df_filtered = df_filtered[df_filtered[filter_name].isin(filter_value)]
                            
                            elif filter_info["type"] == "toggle" and filter_value:
                                df_filtered = df_filtered[df_filtered[filter_name] == True]

        # UNA SOLA TABLA
        sel = st.session_state._col_sel
        if not sel:
            st.warning("Selecciona al menos una columna.")
            st.stop()
        df_sel = df_filtered[sel]

        # Render de la tabla con paginación
        total = len(df_sel)
        page = st.session_state.page
        rpp = st.session_state.rows_per_page_db
        start, end = (page-1)*rpp, page*rpp
        
        # Mostrar la tabla
        st.dataframe(df_sel.iloc[start:end], use_container_width=True)        
        
        # Selector de filas por página
        rows_per_page = st.selectbox(
            "Filas por página",
            options=[20, 30, 40, 50, 75, 100],
            index=3,  # 3 → valor por defecto 50
            key="rows_per_page_db_selector"  # Clave única para evitar duplicidad
        )
        
        # Actualizar el valor en session_state solo si cambia
        if rows_per_page != st.session_state.rows_per_page_db:
            st.session_state.rows_per_page_db = rows_per_page
            st.rerun()

        # Información de paginación
        st.write(f"Página {page} de {(total-1)//rpp+1} — Filas {start+1}–{min(end,total)} de {total}")
        
        # Botones de navegación
        prev, _, nxt = st.columns([1,8,1])
        with prev:
            st.button("◀ Anterior", on_click=go_prev, key="btn_prev_db")
        with nxt:
            st.button("Siguiente ▶", on_click=lambda: go_next(total), key="btn_next_db")
        
        # Botón para exportar datos
        st.download_button(
            label="📥 Exportar datos filtrados",
            data=df_sel.to_csv(index=False).encode('utf-8'),
            file_name=f"jugadores_filtrados_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Función para mostrar sección de Informes
def show_reports():
    st.header("📝 Informes")
    
    # Tabs para separar entre crear y ver informes
    tab1, tab2 = st.tabs(["Ver Informes", "Crear Informe"])
    
    # Tab 1: Ver informes existentes
    with tab1:
        st.subheader("Informes existentes")
        
        # Filtro de búsqueda por jugador
        player_filter = st.text_input("Buscar por nombre de jugador", key="search_reports")
        
        # Obtener informes de la base de datos
        page = st.session_state.get('reports_page', 1)
        reports_per_page = 10
        offset = (page - 1) * reports_per_page
        
        reports, total_reports = get_reports_from_db(
            limit=reports_per_page,
            offset=offset,
            player_filter=player_filter if player_filter else None
        )
        
        if not reports:
            st.info("No hay informes disponibles.")
        else:
            # Mostrar informes en forma de tarjetas
            for report in reports:
                with st.container():
                    cols = st.columns([3, 2, 1])
                    
                    with cols[0]:
                        st.markdown(f"""
                        <div style='background-color: #1E1E1E; padding: 15px; border-radius: 5px;'>
                            <h3>{report['player_name']}</h3>
                            <p><strong>Equipo:</strong> {report['player_club']}</p>
                            <p><strong>Posición:</strong> {report['position']}</p>
                            <p><strong>Partido:</strong> {report['local_team']} vs {report['visitor_team']} ({report['result']})</p>
                            <p><strong>Fecha:</strong> {report['match_date']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with cols[1]:
                        st.markdown(f"""
                        <div style='background-color: #1E1E1E; padding: 15px; border-radius: 5px; height: 90%;'>
                            <p><strong>Valoración:</strong> {report['overall_rating']}/10</p>
                            <p><strong>Minutos:</strong> {report['minutes_played']}</p>
                            <p><strong>Scout:</strong> {report['scout_name']}</p>
                            <p><strong>Creado:</strong> {report['created_at']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with cols[2]:
                        if st.button("Ver detalle", key=f"view_report_{report['id']}"):
                            st.session_state.view_report_id = report['id']
                            st.rerun()
                        
                        # Generar PDF
                        report_data = get_report_by_id(report['id'])
                        if report_data:
                            pdf_buffer = generate_report_pdf(report_data)
                            if pdf_buffer:
                                st.download_button(
                                    label="Descargar PDF",
                                    data=pdf_buffer,
                                    file_name=f"informe_{report_data['player_name'].replace(' ', '_')}_{report_data['match_date'].replace('/', '-')}.pdf",
                                    mime="application/pdf",
                                    key=f"download_report_{report['id']}"
                                )
                
                st.markdown("---")
            
            # Paginación
            total_pages = (total_reports - 1) // reports_per_page + 1
            
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if st.button("◀ Anterior") and page > 1:
                        st.session_state.reports_page = page - 1
                        st.rerun()
                
                with col2:
                    st.write(f"Página {page} de {total_pages}")
                
                with col3:
                    if st.button("Siguiente ▶") and page < total_pages:
                        st.session_state.reports_page = page + 1
                        st.rerun()
        
        # Vista detallada de un informe
        if 'view_report_id' in st.session_state:
            report_data = get_report_by_id(st.session_state.view_report_id)
            
            if report_data:
                # Crear una ventana modal (usando st.expander como alternativa)
                with st.expander("Detalles del informe", expanded=True):
                    st.markdown(f"# Informe: {report_data['player_name']}")
                    
                    # Información del partido
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Datos del partido")
                        st.markdown(f"**Fecha:** {report_data['match_date']}")
                        st.markdown(f"**Equipos:** {report_data['local_team']} vs {report_data['visitor_team']}")
                        st.markdown(f"**Resultado:** {report_data['result']}")
                    
                    with col2:
                        st.markdown("### Datos del jugador")
                        st.markdown(f"**Jugador:** {report_data['player_name']}")
                        st.markdown(f"**Club:** {report_data['player_club']}")
                        st.markdown(f"**Posición:** {report_data['position']}")
                        st.markdown(f"**Valoración:** {report_data['overall_rating']}/10")
                        st.markdown(f"**Titular:** {'Sí' if report_data['is_starter'] else 'No'}")
                        st.markdown(f"**Minutos jugados:** {report_data['minutes_played']}")
                    
                    # Aspectos técnicos y tácticos
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Aspectos Técnicos")
                        st.write(report_data['technical_aspects'])
                    
                    with col2:
                        st.markdown("### Aspectos Tácticos")
                        st.write(report_data['tactical_aspects'])
                    
                    # Aspectos físicos y psicológicos
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Aspectos Físicos")
                        st.write(report_data['physical_aspects'])
                    
                    with col2:
                        st.markdown("### Aspectos Psicológicos")
                        st.write(report_data['psychological_aspects'])
                    
                    # Observaciones
                    st.markdown("### Observaciones")
                    st.write(report_data['observations'])
                    
                    # Mostrar foto si existe
                    if report_data['photo_path'] and os.path.exists(report_data['photo_path']):
                        st.image(report_data['photo_path'], caption=f"Foto de {report_data['player_name']}")
                    
                    # Botón para volver a la lista
                    if st.button("Volver a la lista"):
                        del st.session_state.view_report_id
                        st.rerun()
                    
                    # Botón para descargar PDF
                    pdf_buffer = generate_report_pdf(report_data)
                    if pdf_buffer:
                        st.download_button(
                            label="Descargar PDF",
                            data=pdf_buffer,
                            file_name=f"informe_{report_data['player_name'].replace(' ', '_')}_{report_data['match_date'].replace('/', '-')}.pdf",
                            mime="application/pdf"
                        )
    
    # Tab 2: Crear nuevo informe
    with tab2:
        st.subheader("Crear nuevo informe de scouting")
        
        # Formulario para el informe
        with st.form("nuevo_informe"):
            # Datos del partido
            st.markdown("### Datos del partido")
            col1, col2 = st.columns(2)
            
            with col1:
                match_date = st.date_input("Fecha del partido", key="match_date")
                local_team = st.text_input("Equipo local", key="local_team")
                result = st.text_input("Resultado (ej: 2-1)", key="result")
            
            with col2:
                report_date = st.date_input("Fecha del informe", datetime.datetime.now(), key="report_date")
                visitor_team = st.text_input("Equipo visitante", key="visitor_team")
            
            # Datos del jugador
            st.markdown("### Datos del jugador")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                player_name = st.text_input("Nombre del jugador", key="player_name")
            
            with col2:
                player_club = st.text_input("Club del jugador", key="player_club")
            
            with col3:
                position = st.selectbox(
                    "Posición",
                    ["Portero", "Defensa central", "Lateral derecho", "Lateral izquierdo", 
                     "Mediocentro defensivo", "Mediocentro", "Mediocentro ofensivo", 
                     "Extremo derecho", "Extremo izquierdo", "Mediapunta", "Delantero centro"],
                    key="position"
                )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                overall_rating = st.slider("Valoración general", 1, 10, 5, key="overall_rating")
            
            with col2:
                is_starter = st.checkbox("Titular", True, key="is_starter")
            
            with col3:
                minutes_played = st.number_input("Minutos jugados", 0, 120, 90, key="minutes_played")
            
            # Aspectos del jugador
            st.markdown("### Evaluación del jugador")
            
            technical_aspects = st.text_area(
                "Aspectos técnicos",
                "Análisis de los aspectos técnicos del jugador...",
                height=150,
                key="technical_aspects"
            )
            
            tactical_aspects = st.text_area(
                "Aspectos tácticos",
                "Análisis de los aspectos tácticos del jugador...",
                height=150,
                key="tactical_aspects"
            )
            
            physical_aspects = st.text_area(
                "Aspectos físicos",
                "Análisis de los aspectos físicos del jugador...",
                height=150,
                key="physical_aspects"
            )
            
            psychological_aspects = st.text_area(
                "Aspectos psicológicos",
                "Análisis de los aspectos psicológicos del jugador...",
                height=150,
                key="psychological_aspects"
            )
            
            observations = st.text_area(
                "Observaciones",
                "Observaciones adicionales...",
                height=150,
                key="observations"
            )
            
            # Subida de foto
            st.markdown("### Foto del jugador (opcional)")
            player_photo = st.file_uploader("Subir foto del jugador", type=["jpg", "jpeg", "png"])
            
            # Botón de enviar
            submit_button = st.form_submit_button("Guardar informe")
        
        # Procesar el formulario
        if submit_button:
            # Validar campos obligatorios
            required_fields = [
                (player_name, "Nombre del jugador"),
                (player_club, "Club del jugador"),
                (local_team, "Equipo local"),
                (visitor_team, "Equipo visitante"),
                (result, "Resultado")
            ]
            
            missing_fields = [field_name for value, field_name in required_fields if not value]
            
            if missing_fields:
                st.error(f"Por favor, completa los siguientes campos obligatorios: {', '.join(missing_fields)}")
            else:
                # Guardar la foto si existe
                photo_path = None
                if player_photo:
                    # Crear directorio de fotos si no existe
                    photos_dir = REPORTS_DIR / "photos"
                    photos_dir.mkdir(exist_ok=True)
                    
                    # Generar nombre único para el archivo
                    file_ext = os.path.splitext(player_photo.name)[1]
                    photo_filename = f"{player_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
                    photo_path = str(photos_dir / photo_filename)
                    
                    # Guardar archivo
                    with open(photo_path, "wb") as f:
                        f.write(player_photo.getbuffer())
                
                # Crear diccionario con los datos del informe
                report_data = {
                    'report_date': report_date.strftime("%d/%m/%Y"),
                    'match_date': match_date.strftime("%d/%m/%Y"),
                    'local_team': local_team,
                    'visitor_team': visitor_team,
                    'result': result,
                    'player_name': player_name,
                    'player_club': player_club,
                    'position': position,
                    'overall_rating': overall_rating,
                    'is_starter': is_starter,
                    'minutes_played': minutes_played,
                    'technical_aspects': technical_aspects,
                    'tactical_aspects': tactical_aspects,
                    'physical_aspects': physical_aspects,
                    'psychological_aspects': psychological_aspects,
                    'observations': observations,
                    'photo_path': photo_path,
                    'created_by': st.session_state.user_id
                }
                
                # Guardar en la base de datos
                report_id = save_report_to_db(report_data)
                
                if report_id:
                    st.success(f"Informe guardado correctamente con ID: {report_id}")
                    
                    # Generar PDF y ofrecer descarga
                    pdf_buffer = generate_report_pdf(report_data)
                    if pdf_buffer:
                        st.download_button(
                            label="Descargar informe en PDF",
                            data=pdf_buffer,
                            file_name=f"informe_{player_name.replace(' ', '_')}_{match_date.strftime('%d-%m-%Y')}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.error("Error al guardar el informe. Inténtalo de nuevo.")

# Función para descargar fuentes Roboto (opcional)
def download_roboto_fonts():
    """
    Descarga las fuentes Roboto si no existen en la carpeta de fuentes.
    """
    try:
        import requests
        
        font_urls = {
            "Roboto-Regular.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf",
            "Roboto-Bold.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf",
            "Roboto-Thin.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Thin.ttf"
        }
        
        for font_name, url in font_urls.items():
            font_path = FONTS_DIR / font_name
            if not font_path.exists():
                response = requests.get(url)
                if response.status_code == 200:
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    st.info(f"Fuente {font_name} descargada correctamente.")
                else:
                    st.warning(f"No se pudo descargar la fuente {font_name}.")
    except Exception as e:
        st.warning(f"Error al descargar fuentes: {e}")

# Función para mostrar sección de Visualizaciones (corregida e integrada)
def show_visualizations():
    st.header("📈 Visualizaciones")
    st.write("Aquí puedes generar visualizaciones a partir de los datos de los jugadores.")
    
    # Selector de competición
    comp_options = {
        "Todas": "wyscout_1ra_2da_RFEF_limpio.xlsx",
        "1ra RFEF": "wyscout_1ra_RFEF_limpio.xlsx",
        "2da RFEF": "wyscout_2da_RFEF_limpio.xlsx"
    }
    
    comp = st.selectbox("Competición", list(comp_options.keys()), key="viz_comp")
    
    # Cargar datos según competición seleccionada
    data_file = comp_options[comp]
    data_path = DATA_DIR / data_file
    
    if not data_path.exists():
        st.error(f"Archivo no encontrado: {data_file}. Por favor, asegúrate de que existe en la carpeta 'data'.")
        # Intentar cargar cualquier archivo disponible
        excel_files = list(DATA_DIR.glob("*.xlsx"))
        if excel_files:
            data_path = excel_files[0]
            st.warning(f"Se cargará un archivo alternativo: {data_path.name}")
        else:
            st.stop()
    
    df = load_specific_data(data_path)
    
    if df.empty:
        st.warning("No hay datos disponibles. Por favor, comprueba los archivos en la carpeta 'data'.")
        st.stop()
    
    # Comprobar si existen las fuentes Roboto y mostrar botón para descargarlas si no existen
    if not (FONTS_DIR / 'Roboto-Regular.ttf').exists():
        if st.button("Descargar fuentes Roboto (mejora los gráficos)"):
            download_roboto_fonts()
    
    # Mostrar información del dataset
    st.write(f"Dataset cargado: {df.shape[0]} jugadores, {df.shape[1]} columnas")
    
    # Tabs para diferentes tipos de visualizaciones
    viz_tabs = st.tabs(["Radar Chart", "Comparativa", "Ranking"])
    
    # Tab 1: Radar Chart (Mejorado)
    with viz_tabs[0]:
        st.subheader("Radar Chart")
        
        # Verificar que exista la columna 'jugador'
        if 'jugador' not in df.columns:
            st.error("El DataFrame no contiene la columna 'jugador'. Por favor, revisa la estructura de los datos.")
            st.stop()
        
        # Seleccionar jugador
        all_players = sorted(df['jugador'].unique())
        selected_player = st.selectbox("Seleccionar jugador", all_players, key="radar_player")
        
        if selected_player:
            # Información del jugador
            player_info = df[df['jugador'] == selected_player].iloc[0]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'equipo' in player_info:
                    st.write(f"**Equipo:** {player_info['equipo']}")
            
            with col2:
                if 'pos' in player_info:
                    st.write(f"**Posición:** {player_info['pos']}")
            
            with col3:
                if 'edad' in player_info:
                    st.write(f"**Edad:** {player_info['edad']}")
        
        # Filtrar métricas por grupos
        viz_metrics_groups = {
            "ATAQUE": [
                "goles/90", "xg/90", "remates/90", "remates_port_pct", 
                "regates/90", "regates_pct", "toques_area_pen/90"
            ],
            "PASES": [
                "pases/90", "pases_pct", "pases_prog/90", "jugadas_claves/90", 
                "asis/90", "xa/90", "pases_prof/90"
            ],
            "DEFENSA": [
                "duelos_def/90", "duelos_def_w_pct", "duelos_aer/90", 
                "duelos_aer_w_pct", "entradas/90", "interc/90"
            ],
            "PORTERO": [
                "paradas_pct", "goles_evit/90", "salidas/90", 
                "duelos_aer_portero/90"
            ]
        }
        
        # Seleccionar grupo de métricas
        selected_metrics_group = st.selectbox(
            "Seleccionar grupo de métricas", 
            list(viz_metrics_groups.keys()),
            key="radar_metrics_group"
        )
        
        # Obtener métricas del grupo seleccionado que existan en el dataframe
        available_metrics = [m for m in viz_metrics_groups[selected_metrics_group] if m in df.columns]
        
        # Si no hay métricas disponibles, mostrar mensaje
        if not available_metrics:
            st.warning(f"No hay métricas disponibles para el grupo {selected_metrics_group}")
        else:
            st.write(f"Métricas seleccionadas: {', '.join(available_metrics)}")
            
            # Selector para el tipo de visualización
            chart_type = st.radio(
                "Tipo de visualización",
                ["mplsoccer", "plotly"],
                horizontal=True,
                key="radar_chart_type"
            )
            
            # Lógica condicional para elegir el tipo de gráfico
            if chart_type == "mplsoccer":
                # Generar y mostrar el radar chart con mplsoccer
                with st.spinner("Generando radar chart..."):
                    from visualization_utils import generate_mplsoccer_radar
                    radar_fig = generate_mplsoccer_radar(df, available_metrics, selected_player)
                    if radar_fig:
                        st.pyplot(radar_fig)
                    else:
                        st.error("No se pudo generar el radar chart. Verifica las métricas y los datos.")
            else:
                # Generar y mostrar el radar chart con plotly (original)
                with st.spinner("Generando radar chart..."):
                    from visualization_utils import generate_radar_chart
                    radar_fig = generate_radar_chart(df, available_metrics, selected_player)
                    if radar_fig:
                        st.plotly_chart(radar_fig, use_container_width=True)
                    else:
                        st.error("No se pudo generar el radar chart. Verifica las métricas y los datos.")
            
            # Tabla con los valores concretos
            if st.checkbox("Mostrar valores", value=True):
                player_data = df[df['jugador'] == selected_player][['jugador'] + available_metrics]
                st.dataframe(player_data, use_container_width=True)
    
    # Tab 2: Comparativa de jugadores (Mejorada)
    with viz_tabs[1]:
        st.subheader("Comparativa de jugadores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleccionar jugadores para comparar
            comp_players = st.multiselect(
                "Seleccionar jugadores para comparar",
                all_players,
                key="comp_players"
            )
        
        with col2:
            # Seleccionar grupo de métricas
            comp_metrics_group = st.selectbox(
                "Seleccionar grupo de métricas",
                list(viz_metrics_groups.keys()),
                key="comp_metrics_group"
            )
            
            # Obtener métricas del grupo seleccionado
            comp_available_metrics = [m for m in viz_metrics_groups[comp_metrics_group] if m in df.columns]
        
        # Generar tabla comparativa
        if comp_players and comp_available_metrics:
            comp_table = generate_comparison_table(df, comp_available_metrics, comp_players)
            if comp_table is not None:
                st.dataframe(comp_table, use_container_width=True)
                
                # Opción para descargar la comparativa
                csv = comp_table.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar comparativa",
                    data=csv,
                    file_name=f"comparativa_{'_'.join(comp_players)}.csv",
                    mime="text/csv"
                )
                
                # Radar chart comparativo
                if len(comp_players) == 2:
                    st.subheader("Radar Chart Comparativo")
                    
                    # Selector para el tipo de visualización
                    comp_chart_type = st.radio(
                        "Tipo de visualización",
                        ["mplsoccer", "plotly"],
                        horizontal=True,
                        key="comp_radar_chart_type"
                    )
                    
                    if comp_chart_type == "mplsoccer":
                        # Generar y mostrar el radar chart comparativo con mplsoccer
                        with st.spinner("Generando radar chart comparativo..."):
                            from visualization_utils import generate_mplsoccer_radar_compare
                            comp_radar_fig = generate_mplsoccer_radar_compare(
                                df, comp_available_metrics, comp_players[0], comp_players[1]
                            )
                            if comp_radar_fig:
                                st.pyplot(comp_radar_fig)
                            else:
                                st.error("No se pudo generar el radar chart comparativo. Verifica las métricas y los datos.")
                    else:
                        # Usar la función generate_advanced_radar_chart para mostrar comparativa con Plotly
                        with st.spinner("Generando radar chart comparativo..."):
                            from visualization_utils import generate_advanced_radar_chart
                            comp_radar_fig = generate_advanced_radar_chart(
                                df, comp_available_metrics, comp_players, normalize=True
                            )
                            if comp_radar_fig:
                                st.plotly_chart(comp_radar_fig, use_container_width=True)
                            else:
                                st.error("No se pudo generar el radar chart comparativo. Verifica las métricas y los datos.")
                
                elif len(comp_players) > 2:
                    st.info("El radar chart comparativo con mplsoccer solo está disponible para 2 jugadores. Para comparar más jugadores, se utilizará el método tradicional.")
                    
                    # Generar radar chart para múltiples jugadores con la función existente
                    with st.spinner("Generando radar chart comparativo..."):
                        from visualization_utils import generate_advanced_radar_chart
                        comp_radar_fig = generate_advanced_radar_chart(
                            df, comp_available_metrics, comp_players, normalize=True
                        )
                        if comp_radar_fig:
                            st.plotly_chart(comp_radar_fig, use_container_width=True)
                        else:
                            st.error("No se pudo generar el radar chart comparativo.")
        else:
            st.info("Selecciona al menos un jugador y un grupo de métricas para la comparativa.")
    
    # Tab 3: Ranking de jugadores (Sin cambios)
    with viz_tabs[2]:
        st.subheader("Ranking de jugadores")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Seleccionar métrica para ranking
            all_metrics = []
            for metrics_list in viz_metrics_groups.values():
                all_metrics.extend([m for m in metrics_list if m in df.columns])
            
            rank_metric = st.selectbox(
                "Seleccionar métrica para ranking",
                sorted(set(all_metrics)),
                key="rank_metric"
            )
        
        with col2:
            # Filtrar por posición
            all_positions = ["Todas"] + sorted(df['pos'].unique())
            rank_position = st.selectbox(
                "Filtrar por posición",
                all_positions,
                key="rank_position"
            )
        
        with col3:
            # Mínimo de minutos jugados
            min_minutes = st.number_input(
                "Mínimo de minutos jugados",
                0, 5000, 500,
                key="rank_min_minutes"
            )
        
        # Número de jugadores a mostrar
        num_players = st.slider(
            "Número de jugadores a mostrar",
            5, 100, 20,
            key="rank_num_players"
        )
        
        # Generar ranking
        if rank_metric:
            ranking_df = generate_player_ranking(
                df,
                rank_metric,
                min_minutes=min_minutes,
                position=None if rank_position == "Todas" else rank_position,
                limit=num_players
            )
            
            if ranking_df is not None:
                st.dataframe(ranking_df, use_container_width=True)
                
                # Opción para descargar el ranking
                csv = ranking_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar ranking",
                    data=csv,
                    file_name=f"ranking_{rank_metric.replace('/', '_')}.csv",
                    mime="text/csv"
                )
                
                # Visualizar como gráfico de barras
                if st.checkbox("Mostrar como gráfico de barras", True):
                    # Limitar a 15 jugadores para el gráfico
                    plot_df = ranking_df.head(15).copy()
                    
                    # Crear un gráfico de barras
                    bar_fig = px.bar(
                        plot_df,
                        x='jugador',
                        y=rank_metric,
                        color='equipo',
                        labels={'jugador': 'Jugador', rank_metric: rank_metric},
                        title=f"Top {len(plot_df)} jugadores por {rank_metric}"
                    )
                    
                    # Personalizar el gráfico
                    bar_fig.update_layout(
                        xaxis_tickangle=-45,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(bar_fig, use_container_width=True)

# Función para mostrar la sección de Administración
def show_admin():
    st.header("⚙️ Administración")
    
    admin_tabs = st.tabs(["Gestión de usuarios", "Cargar datos", "Configuración"])
    
    # Tab 1: Gestión de usuarios
    with admin_tabs[0]:
        st.subheader("Gestión de usuarios")
        
        # Formulario para crear usuarios
        with st.form("crear_usuario"):
            st.markdown("### Crear nuevo usuario")
            
            username = st.text_input("Nombre de usuario", key="new_username")
            password = st.text_input("Contraseña", type="password", key="new_password")
            role = st.selectbox("Rol", ["scout", "admin"], key="new_role")
            
            submit = st.form_submit_button("Crear usuario")
        
        if submit:
            if not username or not password:
                st.error("Por favor, completa todos los campos")
            else:
                success, message = create_user(username, password, role)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Lista de usuarios existentes
        st.markdown("### Usuarios existentes")
        
        users = get_users()
        if not users:
            st.info("No hay usuarios registrados")
        else:
            for user in users:
                with st.container():
                    cols = st.columns([3, 2, 2, 1])
                    
                    with cols[0]:
                        st.write(f"**{user['username']}**")
                    
                    with cols[1]:
                        st.write(f"Rol: {user['role']}")
                    
                    with cols[2]:
                        st.write(f"Creado: {user['created_at']}")
                    
                    with cols[3]:
                        # No permitir eliminar el usuario actual
                        if user['id'] != st.session_state.user_id:
                            if st.button("Eliminar", key=f"delete_{user['id']}"):
                                success, message = delete_user(user['id'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                
                st.markdown("---")
    
    # Tab 2: Cargar datos
    with admin_tabs[1]:
        st.subheader("Cargar datos de jugadores")
        
        # Subir archivo Excel
        uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
        
        if uploaded_file:
            try:
                # Vista previa de los datos
                df_preview = pd.read_excel(uploaded_file)
                st.write("Vista previa de los datos:")
                st.dataframe(df_preview.head())
                
                # Guardar archivo
                if st.button("Guardar archivo"):
                    # Crear directorio si no existe
                    DATA_DIR.mkdir(exist_ok=True)
                    
                    # Generar nombre de archivo
                    file_name = uploaded_file.name
                    file_path = DATA_DIR / file_name
                    
                    # Guardar
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"Archivo guardado correctamente como {file_name}")
                    
                    # Invalidar caché para recargar datos
                    st.cache_data.clear()
            
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
        
        # Mostrar archivos existentes
        st.subheader("Archivos de datos existentes")
        
        excel_files = list(DATA_DIR.glob("*.xlsx")) + list(DATA_DIR.glob("*.xls"))
        
        if not excel_files:
            st.info("No hay archivos de datos subidos")
        else:
            for file in excel_files:
                cols = st.columns([3, 1, 1])
                
                with cols[0]:
                    st.write(f"**{file.name}**")
                
                with cols[1]:
                    st.write(f"Tamaño: {file.stat().st_size / 1024:.1f} KB")
                
                with cols[2]:
                    if st.button("Eliminar", key=f"delete_file_{file.name}"):
                        try:
                            os.remove(file)
                            st.success(f"Archivo {file.name} eliminado")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar archivo: {e}")
    
    # Tab 3: Configuración
    with admin_tabs[2]:
        st.subheader("Configuración")
        
        # Cambiar contraseña
        with st.form("cambiar_contraseña"):
            st.markdown("### Cambiar contraseña")
            
            current_password = st.text_input("Contraseña actual", type="password", key="current_pwd")
            new_password = st.text_input("Nueva contraseña", type="password", key="new_pwd")
            confirm_password = st.text_input("Confirmar nueva contraseña", type="password", key="confirm_pwd")
            
            submit = st.form_submit_button("Cambiar contraseña")
        
        if submit:
            if not current_password or not new_password or not confirm_password:
                st.error("Por favor, completa todos los campos")
            elif new_password != confirm_password:
                st.error("Las contraseñas no coinciden")
            else:
                # Verificar contraseña actual
                hashed_pwd = hashlib.sha256(current_password.encode()).hexdigest()
                
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM users WHERE id = ? AND password = ?",
                    (st.session_state.user_id, hashed_pwd)
                )
                
                if not cursor.fetchone():
                    st.error("La contraseña actual es incorrecta")
                else:
                    success, message = change_password(st.session_state.user_id, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                
                conn.close()

# Función para cerrar sesión
def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.rerun()

# Aplicación principal
def main():
    # Cargar CSS personalizado
    load_css()
    
    # Mostrar splash screen al inicio
    add_splash_screen()
    
    # Verificar autenticación
    if not check_auth():
        show_login()
        return
    
    # Crear barra lateral para navegación
    with st.sidebar:
        st.image(ASSETS_DIR /"Escudo CAC.png", width=100)
        st.title("CAC Scouting")
        
        # Menú de navegación
        menu_option = st.radio(
            "Navegación",
            ["Inicio", "Base de Datos", "Informes", "Visualizaciones"],
            key="menu"
        )
        
        # Sección de administración solo para admin
        if st.session_state.user_role == "admin":
            if st.checkbox("Administración", key="show_admin"):
                menu_option = "Administración"
        
        # Información del usuario
        st.markdown("---")
        st.write(f"Usuario: **{st.session_state.username}**")
        st.write(f"Rol: **{st.session_state.user_role}**")
        
        # Botón de cerrar sesión
        if st.button("Cerrar sesión"):
            logout()
    
    # Contenido principal según opción seleccionada
    if menu_option == "Inicio":
        show_home()
    elif menu_option == "Base de Datos":
        show_database()
    elif menu_option == "Informes":
        show_reports()
    elif menu_option == "Visualizaciones":
        show_visualizations()
    elif menu_option == "Administración" and st.session_state.user_role == "admin":
        show_admin()

# Punto de entrada
if __name__ == "__main__":
    main()