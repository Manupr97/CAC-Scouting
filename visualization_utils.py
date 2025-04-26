import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from mplsoccer import Radar, grid
import matplotlib.font_manager as fm
from io import BytesIO
import matplotlib as mpl
# Configurar matplotlib para funcionar correctamente con Streamlit
mpl.use('Agg')  # Usar el backend Agg para evitar problemas con Streamlit

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

# Función para generar un radar chart avanzado
def generate_advanced_radar_chart(player_data, metrics, player_names, normalize=True):
    """
    Genera un radar chart para comparar múltiples jugadores en base a métricas seleccionadas.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metrics (list): Lista de métricas a visualizar
        player_names (list): Lista de nombres de jugadores a comparar
        normalize (bool): Si se normalizan los valores entre 0 y 1
        
    Returns:
        plotly.graph_objects.Figure: Figura con el radar chart
    """
    if not player_names or not metrics:
        return None
    
    # Filtrar jugadores
    filtered_data = player_data[player_data['jugador'].isin(player_names)]
    if filtered_data.empty:
        return None
    
    # Verificar que las métricas existen en el dataframe
    available_metrics = [m for m in metrics if m in filtered_data.columns]
    if not available_metrics:
        return None
    
    # Preparar la figura
    fig = go.Figure()
    
    # Colores para los diferentes jugadores
    colors = ['white', 'yellow', 'red', 'blue', 'green', 'purple', 'orange']
    
    # Agregar cada jugador al radar chart
    for i, player in enumerate(player_names):
        player_df = filtered_data[filtered_data['jugador'] == player]
        
        if player_df.empty:
            continue
        
        # Obtener valores para las métricas
        values = []
        for metric in available_metrics:
            if pd.api.types.is_numeric_dtype(player_df[metric]):
                value = player_df[metric].iloc[0]
                
                # Normalizar si es necesario
                if normalize:
                    min_val = player_data[metric].min()
                    max_val = player_data[metric].max()
                    
                    if max_val > min_val:
                        value = (value - min_val) / (max_val - min_val)
                    else:
                        value = 0.5
                
                values.append(value)
            else:
                values.append(0)
        
        # Colores más visibles para los diferentes jugadores (no usar blanco)
    colors = ['#00FFFF', '#FFFF00', '#FF4500', '#1E90FF', '#32CD32', '#FF00FF', '#FFA500']
    
    # [resto del código sin cambios hasta la parte donde se agregan los jugadores]
    
    # Agregar cada jugador al radar chart
    for i, player in enumerate(player_names):
        # [código igual hasta la parte de color]
        
        color = colors[i % len(colors)]  # Usar la nueva paleta de colores
        
        # Usar valores de opacidad directamente
        opacity = 0.3  # Un poco más de opacidad para ver mejor
        
        # Crear un color RGBA basado en el color seleccionado
        if color == '#00FFFF':  # Cyan
            rgba_color = f'rgba(0, 255, 255, {opacity})'
        elif color == '#FFFF00':  # Amarillo
            rgba_color = f'rgba(255, 255, 0, {opacity})'
        elif color == '#FF4500':  # Naranja rojizo
            rgba_color = f'rgba(255, 69, 0, {opacity})'
        elif color == '#1E90FF':  # Azul brillante
            rgba_color = f'rgba(30, 144, 255, {opacity})'
        elif color == '#32CD32':  # Lima verde
            rgba_color = f'rgba(50, 205, 50, {opacity})'
        elif color == '#FF00FF':  # Magenta
            rgba_color = f'rgba(255, 0, 255, {opacity})'
        else:  # Naranja
            rgba_color = f'rgba(255, 165, 0, {opacity})'
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=available_metrics,
            fill='toself',
            name=player,
            line=dict(color=color, width=2),  # Línea más gruesa
            fillcolor=rgba_color
        ))
    
    # Configurar el layout con líneas más visibles
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1] if normalize else None,
                showticklabels=True,  # Mostrar valores
                gridcolor="rgba(255, 255, 255, 0.3)",  # Rejilla más visible
                linecolor="rgba(255, 255, 255, 0.8)"   # Línea más visible
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.3)",  # Rejilla más visible
                linecolor="rgba(255, 255, 255, 0.8)"   # Línea más visible
            ),
            bgcolor="rgba(0, 0, 0, 0)"
        ),
        showlegend=True,
        legend=dict(
            font=dict(color="white", size=12),  # Texto de leyenda más grande
            bgcolor="rgba(30, 30, 30, 0.8)",    # Fondo más oscuro para la leyenda
            bordercolor="white",
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=13),  # Texto más grande
        margin=dict(l=80, r=80, t=30, b=80)  # Más margen abajo para la leyenda
    )
    
    return fig

# Función para generar gráfico de barras comparativo
def generate_bar_comparison(player_data, metric, player_names, sort=True):
    """
    Genera un gráfico de barras para comparar jugadores en una métrica específica.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metric (str): Métrica a comparar
        player_names (list): Lista de nombres de jugadores a comparar
        sort (bool): Si se ordenan las barras por valor
        
    Returns:
        plotly.graph_objects.Figure: Figura con el gráfico de barras
    """
    if not player_names or metric not in player_data.columns:
        return None
    
    # Filtrar jugadores
    filtered_data = player_data[player_data['jugador'].isin(player_names)]
    if filtered_data.empty:
        return None
    
    # Seleccionar solo jugador, equipo y la métrica
    plot_df = filtered_data[['jugador', 'equipo', metric]].copy()
    
    # Ordenar si es necesario
    if sort:
        plot_df = plot_df.sort_values(by=metric, ascending=False)
    
    # Crear el gráfico
    fig = px.bar(
        plot_df,
        x='jugador',
        y=metric,
        color='equipo',
        labels={'jugador': 'Jugador', metric: metric},
        title=f"Comparación de {metric}"
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

# Función para crear una matriz de dispersión para análisis multivariable
def create_scatter_matrix(player_data, metrics, min_minutes=0, position=None, highlighted_players=None):
    """
    Crea una matriz de dispersión para analizar múltiples métricas simultáneamente.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metrics (list): Lista de métricas a visualizar (máximo 4 recomendado)
        min_minutes (int): Minutos mínimos jugados para filtrar jugadores
        position (str): Posición para filtrar jugadores (opcional)
        highlighted_players (list): Lista de jugadores a destacar
        
    Returns:
        plotly.graph_objects.Figure: Figura con la matriz de dispersión
    """
    if len(metrics) < 2:
        return None
    
    # Filtrar por minutos jugados
    filtered_data = player_data[player_data['min'] >= min_minutes].copy()
    
    # Filtrar por posición si se especifica
    if position and position != "Todas":
        filtered_data = filtered_data[filtered_data['pos'] == position]
    
    if filtered_data.empty:
        return None
    
    # Verificar que las métricas existen en el dataframe
    available_metrics = [m for m in metrics if m in filtered_data.columns]
    if len(available_metrics) < 2:
        return None
    
    # Crear la matriz de dispersión
    fig = px.scatter_matrix(
        filtered_data,
        dimensions=available_metrics,
        color='equipo',
        hover_name='jugador',
        labels={col: col for col in available_metrics}
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        title="Matriz de dispersión para análisis multivariable",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Actualizar cada gráfico en la matriz
    fig.update_traces(
        diagonal_visible=False,
        showupperhalf=False,
        marker=dict(size=8, opacity=0.6)
    )
    
    # Destacar jugadores específicos si se proporcionan
    if highlighted_players:
        highlight_data = filtered_data[filtered_data['jugador'].isin(highlighted_players)]
        
        if not highlight_data.empty:
            for i in range(len(available_metrics)):
                for j in range(i):
                    fig.add_trace(
                        go.Scatter(
                            x=highlight_data[available_metrics[j]],
                            y=highlight_data[available_metrics[i]],
                            mode='markers+text',
                            marker=dict(
                                color='red',
                                size=12,
                                line=dict(color='white', width=2)
                            ),
                            text=highlight_data['jugador'],
                            textposition='top center',
                            showlegend=False,
                            hoverinfo='text',
                            hovertext=[
                                f"{row['jugador']} ({row['equipo']})<br>" +
                                f"{available_metrics[j]}: {row[available_metrics[j]]}<br>" +
                                f"{available_metrics[i]}: {row[available_metrics[i]]}"
                                for _, row in highlight_data.iterrows()
                            ]
                        ),
                        row=i+1, col=j+1
                    )
    
    return fig

# Función para generar gráfico de líneas de evolución
def generate_evolution_chart(player_data, player_name, metrics, seasons):
    """
    Genera un gráfico de líneas para mostrar la evolución de un jugador a lo largo de diferentes temporadas.
    
    Args:
        player_data (dict): Diccionario con DataFrames para cada temporada
        player_name (str): Nombre del jugador
        metrics (list): Lista de métricas a visualizar
        seasons (list): Lista de temporadas
        
    Returns:
        plotly.graph_objects.Figure: Figura con el gráfico de líneas
    """
    if not player_name or not metrics or not seasons:
        return None
    
    # Verificar que hay datos para el jugador
    has_player_data = False
    for season in seasons:
        if season in player_data and player_name in player_data[season]['jugador'].values:
            has_player_data = True
            break
    
    if not has_player_data:
        return None
    
    # Preparar los datos para el gráfico
    evolution_data = {
        'temporada': [],
        'métrica': [],
        'valor': []
    }
    
    for season in seasons:
        if season not in player_data:
            continue
        
        df = player_data[season]
        player_df = df[df['jugador'] == player_name]
        
        if player_df.empty:
            continue
        
        for metric in metrics:
            if metric in player_df.columns:
                evolution_data['temporada'].append(season)
                evolution_data['métrica'].append(metric)
                evolution_data['valor'].append(player_df[metric].iloc[0])
    
    if not evolution_data['temporada']:
        return None
    
    # Crear el DataFrame para el gráfico
    evolution_df = pd.DataFrame(evolution_data)
    
    # Crear el gráfico de líneas
    fig = px.line(
        evolution_df,
        x='temporada',
        y='valor',
        color='métrica',
        markers=True,
        title=f"Evolución de {player_name}",
        labels={'temporada': 'Temporada', 'valor': 'Valor', 'métrica': 'Métrica'}
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title='Temporada',
            tickmode='array',
            tickvals=seasons
        )
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=10)
    )
    
    return fig

# Función para generar un mapa de calor de correlaciones
def generate_correlation_heatmap(player_data, metrics, min_minutes=0, position=None):
    """
    Genera un mapa de calor de correlaciones entre diversas métricas.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metrics (list): Lista de métricas a analizar
        min_minutes (int): Minutos mínimos jugados para filtrar jugadores
        position (str): Posición para filtrar jugadores (opcional)
        
    Returns:
        plotly.graph_objects.Figure: Figura con el mapa de calor
    """
    if len(metrics) < 2:
        return None
    
    # Filtrar por minutos jugados
    filtered_data = player_data[player_data['min'] >= min_minutes].copy()
    
    # Filtrar por posición si se especifica
    if position and position != "Todas":
        filtered_data = filtered_data[filtered_data['pos'] == position]
    
    if filtered_data.empty:
        return None
    
    # Verificar que las métricas existen en el dataframe
    available_metrics = [m for m in metrics if m in filtered_data.columns and pd.api.types.is_numeric_dtype(filtered_data[m])]
    if len(available_metrics) < 2:
        return None
    
    # Calcular la matriz de correlación
    corr_matrix = filtered_data[available_metrics].corr()
    
    # Crear mapa de calor
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        labels=dict(x="Métrica", y="Métrica", color="Correlación"),
        x=available_metrics,
        y=available_metrics,
        color_continuous_scale='RdBu_r',
        range_color=[-1, 1]
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        title="Mapa de calor de correlaciones",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

# Función para generar un gráfico de diagrama de caja
def generate_boxplot(player_data, metric, group_by='pos', min_minutes=0):
    """
    Genera un diagrama de caja para comparar distribuciones de una métrica agrupada por una variable.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metric (str): Métrica a visualizar
        group_by (str): Variable para agrupar (por defecto: 'pos')
        min_minutes (int): Minutos mínimos jugados para filtrar jugadores
        
    Returns:
        plotly.graph_objects.Figure: Figura con el diagrama de caja
    """
    if metric not in player_data.columns or group_by not in player_data.columns:
        return None
    
    # Filtrar por minutos jugados
    filtered_data = player_data[player_data['min'] >= min_minutes].copy()
    
    if filtered_data.empty:
        return None
    
    # Crear el diagrama de caja
    fig = px.box(
        filtered_data,
        x=group_by,
        y=metric,
        color=group_by,
        title=f"Distribución de {metric} por {group_by}",
        labels={metric: metric, group_by: group_by}
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    return fig

# Función para generar percentiles de jugador
def generate_player_percentiles(player_data, player_name, metrics, min_minutes=0, position=None):
    """
    Calcula y visualiza los percentiles de un jugador en comparación con otros.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        player_name (str): Nombre del jugador
        metrics (list): Lista de métricas a analizar
        min_minutes (int): Minutos mínimos jugados para filtrar jugadores
        position (str): Posición para filtrar jugadores (opcional)
        
    Returns:
        tuple: (DataFrame con percentiles, plotly.graph_objects.Figure con gráfico)
    """
    if player_name not in player_data['jugador'].values:
        return None, None
    
    # Filtrar por minutos jugados
    filtered_data = player_data[player_data['min'] >= min_minutes].copy()
    
    # Filtrar por posición si se especifica
    if position and position != "Todas":
        filtered_data = filtered_data[filtered_data['pos'] == position]
    else:
        # Si no se especifica posición, filtrar por la posición del jugador
        player_pos = player_data[player_data['jugador'] == player_name]['pos'].iloc[0]
        filtered_data = filtered_data[filtered_data['pos'] == player_pos]
    
    if filtered_data.empty:
        return None, None
    
    # Verificar que las métricas existen en el dataframe
    available_metrics = [m for m in metrics if m in filtered_data.columns and pd.api.types.is_numeric_dtype(filtered_data[m])]
    if not available_metrics:
        return None, None
    
    # Obtener datos del jugador
    player_df = filtered_data[filtered_data['jugador'] == player_name]
    if player_df.empty:
        return None, None
    
    # Calcular percentiles
    percentiles = {}
    for metric in available_metrics:
        player_value = player_df[metric].iloc[0]
        percentile = (filtered_data[metric] <= player_value).mean() * 100
        percentiles[metric] = percentile
    
    # Crear DataFrame de percentiles
    percentile_df = pd.DataFrame({
        'Métrica': list(percentiles.keys()),
        'Percentil': list(percentiles.values()),
        'Valor': [player_df[m].iloc[0] for m in percentiles.keys()]
    })
    
    # Ordenar por percentil
    percentile_df = percentile_df.sort_values('Percentil', ascending=False)
    
    # Crear gráfico de barras horizontales
    fig = px.bar(
        percentile_df,
        y='Métrica',
        x='Percentil',
        orientation='h',
        title=f"Percentiles de {player_name}",
        labels={'Percentil': 'Percentil', 'Métrica': 'Métrica'},
        text='Valor'
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title='Percentil',
            range=[0, 100]
        ),
        yaxis=dict(
            title='',
            autorange='reversed'
        )
    )
    
    # Personalizar barras según percentil
    fig.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside',
        marker=dict(
            color=[
                'red' if p < 25 else
                'yellow' if p < 50 else
                'lightgreen' if p < 75 else
                'green'
                for p in percentile_df['Percentil']
            ]
        )
    )
    
    return percentile_df, fig

def generate_mplsoccer_radar(player_data, metrics, player_name, show_title=True):
    """
    Genera un radar chart para un jugador utilizando mplsoccer.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metrics (list): Lista de métricas a visualizar
        player_name (str): Nombre del jugador a mostrar
        show_title (bool): Si se muestra el título del gráfico
        
    Returns:
        matplotlib.figure.Figure: Figura con el radar chart o None si hay error
    """
    try:
        # Verificar que existe el jugador
        if player_name not in player_data['jugador'].values:
            st.error(f"Jugador '{player_name}' no encontrado en los datos")
            return None
            
        # Filtrar jugador seleccionado
        player_info = player_data[player_data['jugador'] == player_name].iloc[0]
        
        # Verificar que existen las métricas
        available_metrics = [m for m in metrics if m in player_data.columns]
        if not available_metrics:
            st.error("Ninguna de las métricas seleccionadas está disponible en los datos")
            return None
        
        # Limpia los nombres de las métricas para evitar problemas de parseo
        clean_metrics = [m.replace('/', '_per_').replace('-', '_') for m in available_metrics]
        metrics_map = dict(zip(clean_metrics, available_metrics))
        
        # Preparar datos para el radar chart
        params = clean_metrics
        values = []
        
        # Calcular rangos (mínimo y máximo) para cada métrica
        min_ranges = []
        max_ranges = []
        
        for clean_metric, original_metric in metrics_map.items():
            if pd.api.types.is_numeric_dtype(player_data[original_metric]):
                min_val = player_data[original_metric].min()
                max_val = player_data[original_metric].max()
                
                # Añadir un pequeño margen al máximo
                margin = (max_val - min_val) * 0.05
                min_ranges.append(min_val)
                max_ranges.append(max_val + margin)
                
                # Obtener el valor del jugador
                val = player_info[original_metric]
                values.append(val)
            else:
                # Si no es numérico, excluirlo
                idx = params.index(clean_metric)
                params.pop(idx)
                del metrics_map[clean_metric]
        
        if not params:
            st.error("No hay métricas numéricas disponibles")
            return None
        
        # Crear objeto Radar con listas separadas para min_range y max_range
        radar = Radar(params=params, min_range=min_ranges, max_range=max_ranges,
                     round_int=[False] * len(params), num_rings=4, 
                     ring_width=1, center_circle_radius=1)
        
        # Crear figura y ejes
        fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                        title_space=0, endnote_space=0, grid_key='radar', axis=False)
        
        # Configurar el eje como radar
        radar.setup_axis(ax=axs['radar'])
        
        # Dibujar círculos internos con colores más visibles
        rings_inner = radar.draw_circles(ax=axs['radar'], 
                                        facecolor='#1E1E1E',  # Mantener el fondo oscuro
                                        edgecolor='#888888')  # Círculos más visibles en gris
        
        # Dibujar el radar con color más brillante
        # draw_radar ahora devuelve una tupla (poly, rings, vertices)
        radar_poly, rings_outer, vertices = radar.draw_radar(
            values,
            ax=axs['radar'],
            kwargs_radar={'facecolor': '#aa65b2', 'alpha': 0.7},
            kwargs_rings={'facecolor': '#66d8ba', 'alpha': 0.3}
        )
        
        # Dibujar etiquetas de rango y parámetros con color más visible
        range_labels = radar.draw_range_labels(ax=axs['radar'], 
                                            fontsize=15, 
                                            color='#CCCCCC')  # Color gris claro para números
        param_labels = radar.draw_param_labels(ax=axs['radar'], 
                                            fontsize=15, 
                                            color='#FFFFFF')  # Color blanco para las etiquetas
        
        # Añadir puntos en los vértices más grandes
        axs['radar'].scatter(vertices[:, 0], vertices[:, 1], c='#aa65b2', 
                        edgecolors='#FFFFFF', marker='o', s=100, zorder=2)  # Puntos más grandes
        
        # Si se muestra el título, añadir textos de título
        if show_title:
            # Obtener equipo y posición si están disponibles
            team = player_info.get('equipo', '')
            position = player_info.get('pos', '')
            
            title1_text = axs['title'].text(0.01, 0.65, player_name, fontsize=25,
                                          ha='left', va='center', color='white')
            title2_text = axs['title'].text(0.01, 0.25, team, fontsize=20,
                                          ha='left', va='center', color='#FFFFFF')
            title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize=25,
                                          ha='right', va='center', color='white')
            title4_text = axs['title'].text(0.99, 0.25, position, fontsize=20,
                                          ha='right', va='center', color='#FFFFFF')
        
        # Configurar colores de fondo
        fig.set_facecolor('#0E1117')
        axs['radar'].set_facecolor('#0E1117')
        if 'title' in axs:
            axs['title'].set_facecolor('#0E1117')
        if 'endnote' in axs:
            axs['endnote'].set_facecolor('#0E1117')
            # Añadir nota del creador
            axs['endnote'].text(0.99, 0.5, 'CAC Scouting', fontsize=15,
                             ha='right', va='center', color='white')
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar radar chart: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

def generate_mplsoccer_radar_compare(player_data, metrics, player_name1, player_name2):
    """
    Genera un radar chart comparativo entre dos jugadores utilizando mplsoccer.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metrics (list): Lista de métricas a visualizar
        player_name1 (str): Nombre del primer jugador
        player_name2 (str): Nombre del segundo jugador
        
    Returns:
        matplotlib.figure.Figure: Figura con el radar chart o None si hay error
    """
    try:
        # Verificar que existen los jugadores
        if player_name1 not in player_data['jugador'].values:
            st.error(f"Jugador '{player_name1}' no encontrado en los datos")
            return None
        if player_name2 not in player_data['jugador'].values:
            st.error(f"Jugador '{player_name2}' no encontrado en los datos")
            return None
            
        # Filtrar jugadores seleccionados
        player_info1 = player_data[player_data['jugador'] == player_name1].iloc[0]
        player_info2 = player_data[player_data['jugador'] == player_name2].iloc[0]
        
        # Verificar que existen las métricas
        available_metrics = [m for m in metrics if m in player_data.columns]
        if not available_metrics:
            st.error("Ninguna de las métricas seleccionadas está disponible en los datos")
            return None
        
        # Limpia los nombres de las métricas para evitar problemas de parseo
        clean_metrics = [m.replace('/', '_per_').replace('-', '_') for m in available_metrics]
        metrics_map = dict(zip(clean_metrics, available_metrics))
        
        # Preparar datos para el radar chart
        params = clean_metrics
        values1 = []
        values2 = []
        
        # Calcular rangos (mínimo y máximo) para cada métrica
        min_ranges = []
        max_ranges = []
        
        for clean_metric, original_metric in metrics_map.items():
            if pd.api.types.is_numeric_dtype(player_data[original_metric]):
                min_val = player_data[original_metric].min()
                max_val = player_data[original_metric].max()
                
                # Añadir un pequeño margen al máximo
                margin = (max_val - min_val) * 0.05
                min_ranges.append(min_val)
                max_ranges.append(max_val + margin)
                
                # Obtener los valores de los jugadores
                val1 = player_info1[original_metric]
                val2 = player_info2[original_metric]
                values1.append(val1)
                values2.append(val2)
            else:
                # Si no es numérico, excluirlo
                idx = params.index(clean_metric)
                params.pop(idx)
                del metrics_map[clean_metric]
        
        if not params:
            st.error("No hay métricas numéricas disponibles")
            return None
        
        # Crear objeto Radar con listas separadas para min_range y max_range
        radar = Radar(params=params, min_range=min_ranges, max_range=max_ranges,
                     round_int=[False] * len(params), num_rings=4, 
                     ring_width=1, center_circle_radius=1)
        
        # Crear figura y ejes
        fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                        title_space=0, endnote_space=0, grid_key='radar', axis=False)
        
        # Configurar el eje como radar
        radar.setup_axis(ax=axs['radar'])
        
        # Colores más brillantes para ambos jugadores
        color1 = '#00f2c1'  # Verde azulado brillante (mantener)
        color2 = '#ff3399'  # Rosa intenso (más brillante que el anterior)
        
        # Modificar estos colores para mejorar la visibilidad
        # Dibujar círculos internos con colores más visibles
        rings_inner = radar.draw_circles(ax=axs['radar'], 
                                        facecolor='#1E1E1E',  # Mantener el fondo oscuro
                                        edgecolor='#888888')  # Círculos más visibles en gris
        
        # Dibujar el radar comparativo con colores más brillantes
        # draw_radar_compare devuelve (poly1, poly2, vertices1, vertices2)
        radar_poly1, radar_poly2, vertices1, vertices2 = radar.draw_radar_compare(
            values1, values2, ax=axs['radar'],
            kwargs_radar={'facecolor': color1, 'alpha': 0.7},
            kwargs_compare={'facecolor': color2, 'alpha': 0.7}
        )

        
        # Dibujar etiquetas de rango y parámetros con color más visible
        range_labels = radar.draw_range_labels(ax=axs['radar'], 
                                            fontsize=15, 
                                            color='#CCCCCC')  # Color gris claro para números
        param_labels = radar.draw_param_labels(ax=axs['radar'], 
                                            fontsize=15, 
                                            color='#FFFFFF')  # Color blanco para las etiquetas
        
        # Añadir puntos en los vértices más grandes
        axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1], c=color1, 
                        edgecolors='#FFFFFF', marker='o', s=100, zorder=2)  # Puntos más grandes
        axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1], c=color2, 
                        edgecolors='#FFFFFF', marker='o', s=100, zorder=2)  # Puntos más grandes
        
        # Añadir títulos
        # Obtener equipos de los jugadores
        team1 = player_info1.get('equipo', '')
        team2 = player_info2.get('equipo', '')
        
        title1_text = axs['title'].text(0.01, 0.65, player_name1, fontsize=25, color='#00f2c1',
                                     ha='left', va='center')
        title2_text = axs['title'].text(0.01, 0.25, team1, fontsize=20, color='#00f2c1',
                                     ha='left', va='center')
        title3_text = axs['title'].text(0.99, 0.65, player_name2, fontsize=25, color='#d80499',
                                     ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, team2, fontsize=20, color='#d80499',
                                     ha='right', va='center')
        
        # Configurar colores de fondo
        fig.set_facecolor('#0E1117')
        axs['radar'].set_facecolor('#0E1117')
        if 'title' in axs:
            axs['title'].set_facecolor('#0E1117')
        if 'endnote' in axs:
            axs['endnote'].set_facecolor('#0E1117')
            # Añadir nota del creador
            axs['endnote'].text(0.99, 0.5, 'CAC Scouting', fontsize=15,
                             ha='right', va='center', color='white')
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar radar chart comparativo: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None
    
# Función mejorada para generar radar chart
def generate_radar_chart(player_data, metrics, player_name=None):
    """
    Genera un radar chart para el jugador seleccionado según las métricas proporcionadas.
    
    Args:
        player_data (DataFrame): DataFrame con los datos de los jugadores
        metrics (list): Lista de métricas a visualizar
        player_name (str, optional): Nombre del jugador a mostrar
        
    Returns:
        plotly.graph_objects.Figure: Figura con el radar chart o None si hay error
    """
    # Verificar que existe el jugador si se proporciona nombre
    if player_name:
        if 'jugador' not in player_data.columns:
            st.error("El DataFrame no contiene la columna 'jugador'")
            return None
            
        if player_name not in player_data['jugador'].values:
            st.error(f"Jugador '{player_name}' no encontrado en los datos")
            return None
        
        # Filtrar solo el jugador seleccionado
        filtered_data = player_data[player_data['jugador'] == player_name].copy()
    else:
        # Si no se proporciona jugador, usar todo el DataFrame
        filtered_data = player_data.copy()
    
    # Verificar que hay datos
    if filtered_data.empty:
        st.error("No hay datos para generar el gráfico")
        return None
    
    # Verificar que existen las métricas en el DataFrame
    available_metrics = []
    for metric in metrics:
        if metric in filtered_data.columns:
            if pd.api.types.is_numeric_dtype(filtered_data[metric]):
                available_metrics.append(metric)
            else:
                st.warning(f"La métrica '{metric}' no es numérica y será ignorada")
        else:
            st.warning(f"La métrica '{metric}' no existe en los datos y será ignorada")
    
    if not available_metrics:
        st.error("No hay métricas válidas para generar el radar chart")
        return None
    
    # Obtener los valores para cada métrica
    values = []
    for metric in available_metrics:
        # Obtener el valor para el jugador seleccionado
        try:
            value = filtered_data[metric].iloc[0]
            
            # Normalizar al rango 0-1 basado en min-max de todos los jugadores
            min_val = player_data[metric].min()
            max_val = player_data[metric].max()
            
            if pd.isna(value):
                # Valor nulo, usar 0 como valor predeterminado
                normalized = 0
            elif max_val > min_val:
                normalized = (value - min_val) / (max_val - min_val)
            else:
                # Si todos los valores son iguales, usar 0.5 como valor predeterminado
                normalized = 0.5
        except Exception as e:
            st.error(f"Error al procesar la métrica '{metric}': {e}")
            normalized = 0
        
        values.append(normalized)
    
    # Crear el radar chart con Plotly
    try:
        fig = go.Figure()
        
        # Añadir el jugador seleccionado
        player_label = player_name if player_name else filtered_data['jugador'].iloc[0]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=available_metrics,
            fill='toself',
            name=player_label,
            line=dict(color='white', width=2),
            fillcolor='rgba(255, 255, 255, 0.2)'
        ))
        
        # Configurar el layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    showticklabels=False,  # Ocultar valores numéricos
                    gridcolor="rgba(255, 255, 255, 0.2)"
                ),
                angularaxis=dict(
                    gridcolor="rgba(255, 255, 255, 0.2)",
                    linecolor="rgba(255, 255, 255, 0.8)"
                ),
                bgcolor="rgba(0, 0, 0, 0)"
            ),
            showlegend=True,
            legend=dict(
                font=dict(color="white"),
                bgcolor="rgba(0, 0, 0, 0.5)",
                bordercolor="white",
                borderwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=80, r=80, t=30, b=30)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar el radar chart: {e}")
        return None