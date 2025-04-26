# CAC Scouting - Plataforma de Análisis y Seguimiento de Jugadores

## Descripción

CAC Scouting es una aplicación web completa desarrollada con Streamlit para el análisis, seguimiento y elaboración de informes sobre jugadores de fútbol. Diseñada específicamente para scouts y analistas deportivos, esta herramienta permite gestionar bases de datos de jugadores, crear informes detallados, visualizar estadísticas y mantenerse al día con las últimas noticias relacionadas con las competiciones.

## Características Principales

- **Autenticación de usuarios**: Sistema de login con roles diferenciados (scout y administrador)
- **Dashboard de noticias**: Actualización automática de noticias desde BeSoccer para 1ra, 2da y 3ra RFEF
- **Base de datos avanzada**: Filtrado dinámico de jugadores por múltiples parámetros
- **Informes de scouting**: Creación y gestión de informes detallados con formato profesional
- **Visualizaciones estadísticas**: Radar charts, comparativas, rankings y análisis avanzados
- **Exportación a PDF**: Generación de informes en formato PDF descargables
- **Administración de usuarios**: Panel de gestión para usuarios administradores
- **Interfaz elegante**: Diseño intuitivo con los colores corporativos (negro y blanco)

## Requisitos del Sistema

- Python 3.7 o superior
- Conexión a internet para la actualización de noticias
- Permisos de escritura en el directorio de la aplicación

## Instalación

1. Clona o descarga este repositorio:
   ```
   git clone <url-del-repositorio>
   cd cac-scouting
   ```

2. Ejecuta el script de configuración para instalar todas las dependencias:
   ```
   python setup.py
   ```

3. Alternativamente, puedes instalar las dependencias manualmente:
   ```
   pip install -r requirements.txt
   ```

## Estructura de Directorios

```
cac-scouting/
├── New_Web_Scouting.py      # Archivo principal de la aplicación
├── visualization_utils.py   # Utilidades para visualizaciones
├── setup.py                 # Script de configuración
├── requirements.txt         # Dependencias del proyecto
├── data/                    # Archivos Excel con datos de jugadores
├── reports/                 # Informes generados
│   └── photos/              # Fotos de jugadores
├── assets/                  # Recursos gráficos (logo, etc.)
└── db/                      # Base de datos SQLite
```

## Uso

1. Inicia la aplicación con Streamlit:
   ```
   streamlit run New_Web_Scouting.py
   ```

2. Accede a la aplicación en tu navegador (por defecto: http://localhost:8501)

3. Inicia sesión con el usuario administrador predeterminado:
   - Usuario: `admin`
   - Contraseña: `admin123`

4. Una vez dentro, puedes:
   - Crear nuevos usuarios desde el panel de administración
   - Cargar archivos Excel con datos de jugadores
   - Crear y gestionar informes
   - Explorar visualizaciones estadísticas
   - Actualizar noticias de las competiciones

## Datos de Jugadores

La aplicación está diseñada para trabajar con archivos Excel que contengan datos estadísticos de jugadores. Los archivos deben seguir una estructura similar a los siguientes grupos de columnas:

- **GENERAL**: jugador, equipo, pos, pos_secun, pj, min, edad, etc.
- **FASE DEFENSIVA**: duelos_def/90, interc/90, etc.
- **FASE OFENSIVA**: goles, goles/90, xg, xg/90, etc.
- **ORGANIZACIÓN**: asis, asis/90, pases/90, etc.
- **PASES CLAVES**: pases_ult_terc/90, jugadas_claves/90, etc.
- **PORTERO**: goles_recibidos, paradas_pct, etc.
- **BALÓN PARADO**: tiros_libres/90, corners/90, etc.

Los archivos Excel deben colocarse en la carpeta `data/` para que la aplicación pueda acceder a ellos.

## Personalización

- **Logo**: Reemplaza el archivo `assets/logo.png` con tu propio logo (preferiblemente sobre fondo negro)
- **Colores**: La aplicación viene preconfigurada con un tema en blanco y negro, puedes ajustar los colores en el archivo `.streamlit/config.toml`
- **Fuentes de noticias**: Puedes modificar las fuentes de noticias en el código fuente según tus necesidades

## Administración

El panel de administración permite:

1. **Gestionar usuarios**:
   - Crear nuevos scouts o administradores
   - Eliminar usuarios existentes
   - Cambiar contraseñas

2. **Cargar datos**:
   - Subir nuevos archivos Excel
   - Ver y gestionar archivos existentes

3. **Configuración**:
   - Cambiar la contraseña de tu cuenta
   - (Futuras opciones de configuración)

## Informes de Scouting

Los informes de scouting incluyen:

- Datos básicos del partido (fecha, equipos, resultado)
- Información del jugador (nombre, club, posición)
- Valoración general (escala 1-10)
- Aspectos técnicos, tácticos, físicos y psicológicos
- Observaciones adicionales
- Foto del jugador (opcional)

## Visualizaciones

La aplicación ofrece varias visualizaciones estadísticas:

1. **Radar Charts**: Comparación visual de jugadores en múltiples métricas
2. **Comparativas**: Tablas comparativas de jugadores
3. **Rankings**: Clasificación de jugadores según métricas específicas
4. **Análisis avanzados**: Correlaciones, percentiles, evolución de jugadores

## Soporte

Para reportar problemas o solicitar nuevas características, por favor utiliza la sección de Issues del repositorio.

## Desarrollado por

Esta aplicación fue desarrollada para el Club Atlético CAC para facilitar el trabajo de su departamento de scouting.

---

**Nota**: Esta aplicación está diseñada para uso interno y puede requerir adaptaciones específicas para su uso en otros contextos o competiciones.