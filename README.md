# Progreso y Funcionalidad Actual - NeuroCapture

## Descripción General

NeuroCapture es una plataforma integral de captura, procesamiento y análisis de datos neurológicos diseñada para facilitar la evaluación cognitiva y el análisis de características de audio en investigación neurológica. El sistema combina evaluaciones cognitivas tradicionales con análisis avanzado de audio para proporcionar una herramienta completa de evaluación neurológica.

## Arquitectura del Sistema

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI con uvicorn como servidor ASGI
- **Base de datos**: PostgreSQL con AsyncPG como driver asíncrono
- **ORM**: SQLAlchemy con soporte para operaciones asíncronas
- **Migraciones**: Alembic para control de versiones de esquema

### Frontend (Electron + React)
- **Aplicación de escritorio**: Electron para compatibilidad multiplataforma
- **Interfaz de usuario**: React 18 con componentes funcionales
- **Estilado**: TailwindCSS para diseño responsivo y moderno
- **Navegación**: React Router para manejo de rutas
- **Iconografía**: HeroIcons para iconos consistentes

### Infraestructura
- **Containerización**: Docker Compose para orquestación de servicios
- **Almacenamiento**: Sistema de archivos local para grabaciones de audio
- **API**: RESTful con documentación automática (Swagger/OpenAPI)

## Funcionalidades Implementadas

### 1. Gestión de Pacientes

#### Características principales:
- **Creación de pacientes** con identificadores de estudio únicos
- **Edición de información básica** (ID de estudio)
- **Sistema de búsqueda** por identificador de estudio
- **Eliminación segura** con confirmación del usuario
- **Exportación de datos** en formato CSV

#### Campos de datos:
- Identificador de estudio (1-50 caracteres, único)
- Fechas de creación y actualización automáticas
- Relaciones con demografía y evaluaciones

### 2. Datos Demográficos

#### Información capturada:
- **Edad** del participante
- **Género** (selección múltiple)
- **Años de educación** (opcional)
- **Fecha de recolección** de datos
- **Campos ENASEM** (preparado para implementación futura)

#### Funcionalidades:
- Formularios validados con manejo de errores
- Actualización en tiempo real
- Vinculación automática con pacientes

### 3. Evaluaciones Cognitivas

#### Tipos de evaluación soportados:
- **MMSE (Mini-Mental State Examination)**
  - 30 puntos máximo
  - 11 subescalas predefinidas
  - Cálculo automático de puntuaciones

- **MoCA (Montreal Cognitive Assessment)**
  - 30 puntos máximo
  - 8 dominios cognitivos
  - Puntuaciones detalladas por dominio

- **Evaluaciones personalizadas** ("Other")
  - Puntuación flexible
  - Campos personalizables

#### Características avanzadas:
- **Subescalas detalladas** para MMSE y MoCA
- **Fechas y horarios** de evaluación precisos
- **Diagnósticos** asociados (opcionales)
- **Notas clínicas** extensas
- **Edición y eliminación** de evaluaciones existentes

### 4. Procesamiento de Audio

#### Capacidades de grabación:
- **Subida de archivos** de audio en múltiples formatos
- **Metadatos detallados**: tipo de tarea, dispositivo de grabación
- **Vinculación automática** con evaluaciones cognitivas
- **Reproducción integrada** con controles de audio HTML5

#### Procesamiento avanzado de señales:

##### Preprocesamiento:
- **Normalización de audio** con RMS objetivo
- **Reducción de ruido** usando algoritmos de noisereduce
- **Eliminación de picos extremos** para mejorar calidad
- **Conversión de formatos** y frecuencias de muestreo

##### Detección de Actividad Vocal (VAD):
- **WebRTC VAD** con múltiples niveles de agresividad
- **Segmentación automática** de habla y silencio
- **Filtrado por duración mínima** para mayor precisión
- **Umbrales configurables** para diferentes tipos de grabación

### 5. Extracción de Características de Audio

#### Características Prosódicas (35+ características):

##### Temporales:
- **Duración total** de la grabación
- **Conteo de segmentos** de habla y silencio
- **Duraciones promedio** de pausas y habla
- **Variabilidad temporal** (desviación estándar, coeficiente de variación)
- **Relaciones temporales** (habla/pausa, tasa de articulación)

##### Rítmicas:
- **PVI (Pairwise Variability Index)** crudo y normalizado
- **Detección de picos** de intensidad
- **Intervalos entre picos** con estadísticas descriptivas

##### Energéticas:
- **Energía de corto plazo** (media, desviación estándar)
- **Variabilidad energética** (coeficiente de variación)
- **Entropía energética** para análisis de distribución

##### Tempo y Ritmo:
- **Estimación de tempo** en BPM usando librosa
- **Intervalos entre beats** (IBI) con estadísticas completas
- **Análisis de variabilidad rítmica**

#### Características Acústicas (150+ características):

##### Calidad Vocal:
- **Jitter local y PPQ5** para estabilidad de frecuencia
- **Shimmer local y APQ5** para estabilidad de amplitud
- **CPPS (Cepstral Peak Prominence Smoothed)** para calidad vocal

##### Formantes (F1-F4):
- **Estadísticas descriptivas** (media, desviación, rango, mediana)
- **Asimetría y curtosis** para análisis de distribución
- **Derivadas temporales** (delta formantes)
- **Ancho de banda F3** (F3_B3)
- **Coeficiente de variación F4**

##### Espectrales:
- **30 MFCCs** con estadísticas (media, desviación estándar)
- **Delta y Delta-Delta MFCCs** para análisis dinámico
- **Pendiente espectral** para caracterización timbral
- **Centroide espectral** para brillo tonal
- **Flujo espectral** (media y desviación estándar)
- **Roll-off espectral** para análisis de energía
- **Tasa de cruces por cero** para contenido armónico
- **Entropía energética** espectral

##### Armónicos y Ruido:
- **HNR (Harmonics-to-Noise Ratio)** usando autocorrelación
- **AVQI HNR_sd** para análisis de calidad vocal
- **Pitch medio y desviación estándar**

##### Amplitud:
- **Amplitud promedio, pico y varianza**
- **Amplitud mínima y máxima**
- **Diferencia media de amplitud máxima**

##### Complejidad:
- **Dimensión Fractal de Higuchi (HFD)** con múltiples ventanas
- **Estadísticas HFD** (media, máximo, mínimo, desviación, varianza)
- **Características adicionales**: Asimetría, TrajIntra

#### Sistema de Procesamiento en Tiempo Real:

##### Gestión de Tareas:
- **Procesamiento asíncrono** en segundo plano
- **Seguimiento de progreso** en tiempo real (0-100%)
- **Estados de tarea**: pendiente, ejecutándose, completado, fallido
- **Notificaciones** automáticas al usuario

##### Interfaz de Usuario:
- **Barras de progreso** animadas durante procesamiento
- **Indicadores visuales** de estado de extracción
- **Contadores de características** extraídas
- **Botones inteligentes** que se deshabilitan según contexto

##### Almacenamiento:
- **Base de datos relacional** para características extraídas
- **Archivos de audio limpios** guardados automáticamente
- **Metadatos completos** de procesamiento

### 6. Gestión de Datos y Exportación

#### Exportación de Características:
- **Formato CSV** con todas las características
- **Metadatos del paciente** incluidos
- **Información de evaluaciones** asociadas
- **Estructura tabular** para análisis estadístico

#### Integridad de Datos:
- **Eliminación en cascada** para mantener consistencia
- **Validación de tipos** de datos
- **Manejo de valores nulos** y casos extremos
- **Filtrado de características** no válidas (NaN, infinito)

### 7. Interfaz de Usuario

#### Diseño y Experiencia:
- **Navegación por pestañas** intuitiva
- **Formularios responsivos** con validación en tiempo real
- **Tablas interactivas** con ordenamiento y búsqueda
- **Modales y notificaciones** para feedback inmediato
- **Diseño moderno** con TailwindCSS

#### Funcionalidades de Usuario:
- **Búsqueda en tiempo real** de pacientes
- **Edición inline** de datos
- **Confirmaciones de eliminación** para seguridad
- **Indicadores de carga** durante operaciones
- **Tooltips informativos** en botones y campos

## Tecnologías y Librerías Principales

### Procesamiento de Audio:
- **librosa**: Análisis de audio y extracción de características espectrales
- **praat-parselmouth**: Análisis fonético y extracción de formantes
- **noisereduce**: Reducción de ruido avanzada
- **webrtcvad**: Detección de actividad vocal en tiempo real
- **scipy**: Procesamiento de señales y análisis estadístico
- **numpy**: Operaciones matemáticas y manejo de arrays

### Backend:
- **FastAPI**: Framework web moderno con validación automática
- **SQLAlchemy**: ORM con soporte asíncrono
- **Alembic**: Migraciones de base de datos
- **asyncpg**: Driver PostgreSQL asíncrono
- **Pydantic**: Validación de datos y serialización

### Frontend:
- **React 18**: Framework de interfaz de usuario
- **Electron**: Aplicación de escritorio multiplataforma
- **Axios**: Cliente HTTP para comunicación con API
- **TailwindCSS**: Framework de CSS utilitario

## Estado Actual del Desarrollo

### Funcionalidades Completadas ✅:
1. Gestión completa de pacientes
2. Formularios de datos demográficos
3. Sistema de evaluaciones cognitivas (MMSE, MoCA)
4. Subida y reproducción de archivos de audio
5. Procesamiento avanzado de audio con 150+ características
6. Sistema de seguimiento de tareas en tiempo real
7. Exportación de datos en CSV
8. Interfaz de usuario moderna y responsiva
9. Base de datos relacional completa
10. Sistema de notificaciones y validaciones

### En Desarrollo 📋:
1. **Datos de acelerómetro**: Captura y análisis de movimiento
2. **Datos de OpenPose**: Análisis de postura y gestos
3. **Modelos de machine learning**: Predicción automática de diagnósticos
4. **Interpretaciones clínicas**: Sistema de notas e interpretaciones
5. **Campos de ENASEM ** para demografía

## Arquitectura de Base de Datos

### Tablas Principales:
- **patients**: Información básica de participantes
- **demographics**: Datos demográficos detallados
- **cognitive_assessments**: Evaluaciones cognitivas
- **assessment_subscores**: Puntuaciones detalladas por dominio
- **audio_recordings**: Metadatos de grabaciones
- **audio_features**: Características extraídas del audio
- **interpretations**: Notas e interpretaciones clínicas (preparado)
- **model_predictions**: Predicciones de modelos ML (preparado)

### Relaciones:
- Eliminación en cascada para integridad referencial
- Índices optimizados para consultas frecuentes
- Campos de auditoría (created_at, updated_at) en todas las tablas

## Calidad y Robustez del Código

### Testing:
- Tests unitarios para componentes React
- Mocks para APIs y servicios externos
- Validación de flujos de datos críticos

### Manejo de Errores:
- Try-catch comprehensivo en operaciones críticas
- Mensajes de error informativos para usuarios
- Logging detallado para debugging

### Validación de Datos:
- Esquemas Pydantic para validación de entrada
- Validación de archivos de audio
- Sanitización de datos de usuario

---

**Versión del documento**: 1.0  
**Fecha**: 27 Mayo 2025  
**Estado del proyecto**: Beta funcional con características core implementadas
