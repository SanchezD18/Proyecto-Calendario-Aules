# Webcrawler de Aules - Extracción de Entregas y Sincronización con Google Calendar

Herramienta automatizada que extrae las entregas de actividades desde la plataforma Aules y las sincroniza automáticamente con Google Calendar.

## Características

- ✅ Extrae entregas de la cronología de Aules usando Selenium
- ✅ Maneja contenido JavaScript dinámico
- ✅ Extrae fechas, nombres y enlaces de las actividades
- ✅ Sincronización automática con Google Calendar
- ✅ Recordatorios automáticos (1 día antes por email, 1 hora antes por popup)

## Requisitos Previos

1. **Python 3.8 o superior**
2. **Google Chrome** instalado en el sistema
3. **Cuenta de Google** con acceso a Google Calendar API

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Proyecto_webcrawler
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales de Aules

Copia el archivo de ejemplo y completa tus credenciales:

```bash
cp .env.example .env
```

Edita el archivo `.env` y agrega tus credenciales:

```
AULES_USERNAME=tu_usuario
AULES_PASSWORD=tu_contraseña
```

### 4. Configurar Google Calendar API

#### Paso 1: Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Calendar API**:
   - Ve a "APIs y servicios" > "Biblioteca"
   - Busca "Google Calendar API"
   - Haz clic en "Habilitar"

#### Paso 2: Crear credenciales OAuth 2.0

1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "ID de cliente de OAuth"
3. Selecciona "Aplicación de escritorio"
4. Dale un nombre (ej: "Aules Calendar Sync")
5. Descarga el archivo JSON
6. **Renombra el archivo descargado a `credentials.json`**
7. Coloca `credentials.json` en la carpeta del proyecto

#### Paso 3: Configurar pantalla de consentimiento (primera vez)

1. Ve a "APIs y servicios" > "Pantalla de consentimiento de OAuth"
2. Selecciona "Externo" (si es para uso personal) o "Interno" (si tienes Google Workspace)
3. Completa los campos requeridos:
   - Nombre de la aplicación
   - Correo electrónico de soporte
   - Correo del desarrollador
4. Agrega el alcance: `https://www.googleapis.com/auth/calendar`
5. Guarda y continúa

## Uso

Ejecuta el script:

```bash
python webcrawler.py
```

El proceso es el siguiente:

1. **Inicio de sesión**: El script se conecta automáticamente a Aules
2. **Extracción**: Busca y extrae todas las entregas de la cronología
3. **Visualización**: Muestra un resumen de las entregas encontradas con sus fechas
4. **Sincronización**: Pregunta si deseas agregar las entregas a Google Calendar
   - Responde `s` para agregar todas las entregas automáticamente
   - Responde `n` para cancelar la operación

### Primera ejecución con Google Calendar

La primera vez que uses la funcionalidad de Google Calendar:

1. Se abrirá automáticamente tu navegador
2. Inicia sesión con tu cuenta de Google
3. Autoriza el acceso a tu calendario
4. Se generará automáticamente el archivo `token.json` para futuras ejecuciones

## Estructura del Proyecto

```
Proyecto_webcrawler/
├── webcrawler.py          # Script principal
├── calendar_manager.py    # Gestión de Google Calendar
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── .env                   # Credenciales de Aules (no se sube al repo)
├── .env.example           # Ejemplo de archivo .env
├── credentials.json       # Credenciales de Google (no se sube al repo)
└── token.json             # Token de autenticación (no se sube al repo)
```

## Datos Extraídos

Para cada entrega, el script extrae:

- **Nombre**: Nombre de la actividad
- **Fecha completa**: Fecha y hora de entrega
- **Curso**: Módulo o asignatura
- **URL**: Enlace directo a la actividad en Aules
- **ID**: Identificador único de la actividad

## Eventos en Google Calendar

Cada entrega se crea como un evento en tu calendario principal con:

- **Título**: Nombre de la actividad
- **Fecha y hora**: Fecha de vencimiento extraída de Aules
- **Descripción**: Curso, enlace y fecha de entrega
- **Recordatorios**:
  - 1 día antes por email
  - 1 hora antes por popup

## Solución de Problemas

### Error: "ChromeDriver not found"

El script usa `webdriver-manager` que descarga automáticamente ChromeDriver. Si hay problemas:

- Verifica que Chrome esté instalado
- Actualiza Chrome a la última versión

### Error: "No se encontró el archivo credentials.json"

Asegúrate de haber descargado y renombrado el archivo JSON de Google Cloud Console a `credentials.json` y que esté en la carpeta del proyecto.

### Error: "Las variables AULES_USERNAME y AULES_PASSWORD deben estar definidas"

Verifica que el archivo `.env` existe y contiene tus credenciales correctamente.

### No se encuentran entregas

- Verifica que tengas entregas pendientes en tu cronología de Aules
- Asegúrate de tener una conexión estable a internet
- Verifica que tus credenciales sean correctas

### Problemas con Google Calendar API

- Verifica que la API esté habilitada en Google Cloud Console
- Asegúrate de haber completado la pantalla de consentimiento
- Verifica que el archivo `credentials.json` sea válido

## Archivos Generados

- `token.json`: Token de autenticación de Google (se genera automáticamente la primera vez que se usa)

## Notas de Seguridad

⚠️ **IMPORTANTE**: Nunca subas al repositorio:

- El archivo `.env` con tus credenciales
- El archivo `credentials.json` de Google
- El archivo `token.json` de autenticación

Estos archivos están incluidos en `.gitignore` para proteger tu información.

## Licencia

Este proyecto es de uso personal y educativo.
