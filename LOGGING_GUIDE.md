# 📝 Sistema de Logging - Proyecto LSP

## ✅ ¿Qué se agregó?

Se ha implementado un **sistema de logging profesional y centralizado** para facilitar el debugging y seguimiento del proyecto.

---

## 📦 Archivo Principal: `logger_config.py`

### Características:

- ✅ **Logging en consola** con colores
- ✅ **Logging en archivo** con rotación automática (10 MB max, 5 backups)
- ✅ **Timestamps** en todos los mensajes
- ✅ **Diferentes niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Decoradores** para loggear funciones y tiempos de ejecución
- ✅ **Configuración flexible** por módulo

---

## 🚀 Cómo Usar

### 1. Importar en tus scripts

```python
from logger_config import get_logger

# Crear logger para tu módulo
logger = get_logger(__name__)
```

### 2. Loggear mensajes

```python
# Información general
logger.info("Iniciando proceso...")

# Debug (solo visible en modo DEBUG)
logger.debug("Variable x = 42")

# Advertencias
logger.warning("⚠️  Parámetro no especificado, usando default")

# Errores
logger.error("❌ No se pudo abrir archivo")

# Errores con traceback completo
try:
    # código que puede fallar
    pass
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
```

### 3. Usar decoradores

```python
from logger_config import log_function_call, log_execution_time

# Loggear llamadas a función
@log_function_call
def mi_funcion(param1, param2):
    return param1 + param2

# Medir tiempo de ejecución
@log_execution_time
def proceso_lento():
    # código que tarda
    pass
```

---

## 📊 Niveles de Logging

| Nivel | Cuándo usar | Ejemplo |
|-------|-------------|---------|
| **DEBUG** | Información detallada para debugging | `logger.debug("Variable x = 42")` |
| **INFO** | Información general del flujo | `logger.info("Procesando imagen...")` |
| **WARNING** | Advertencias que no detienen la ejecución | `logger.warning("Archivo no encontrado, usando default")` |
| **ERROR** | Errores recuperables | `logger.error("No se pudo procesar frame")` |
| **CRITICAL** | Errores críticos que detienen el programa | `logger.critical("Sistema sin memoria")` |

---

## 📁 Archivos de Log

Los logs se guardan automáticamente en:

```
modelo_lstm_lsp-main/
└── logs/
    ├── lsp_20251014.log        # Log del día actual
    ├── lsp_20251014.log.1      # Backup 1
    ├── lsp_20251014.log.2      # Backup 2
    └── ...
```

### Rotación Automática:
- **Tamaño máximo**: 10 MB por archivo
- **Backups**: 5 archivos anteriores
- **Formato**: `lsp_YYYYMMDD.log`

---

## ⚙️ Configuración

### Cambiar nivel de logging global

```python
from logger_config import set_log_level

# Cambiar a DEBUG para ver más detalles
set_log_level("DEBUG")

# Cambiar a WARNING para ver solo advertencias y errores
set_log_level("WARNING")
```

### Configuración personalizada

```python
from logger_config import setup_logging
import logging

# Setup personalizado
setup_logging(
    log_level=logging.DEBUG,
    console_output=True,     # Mostrar en consola
    file_output=True,        # Guardar en archivo
    colored=True            # Usar colores
)
```

---

## 🎨 Formato de Logs

### En Consola (con colores):
```
2025-10-14 15:30:45 | capture_samples       | INFO     | Iniciando captura de muestras
2025-10-14 15:30:46 | capture_samples       | DEBUG    | Carpeta creada: frame_actions/hola
2025-10-14 15:30:50 | capture_samples       | INFO     | ✓ Muestra #1 guardada: 15 frames
```

### En Archivo:
```
2025-10-14 15:30:45 | capture_samples       | INFO     | Iniciando captura de muestras
2025-10-14 15:30:46 | capture_samples       | DEBUG    | Carpeta creada: frame_actions/hola
2025-10-14 15:30:50 | capture_samples       | INFO     | ✓ Muestra #1 guardada: 15 frames
2025-10-14 15:31:02 | training_model        | ERROR    | Error al cargar datos: archivo no encontrado
Traceback (most recent call last):
  File "training_model.py", line 45, in training_model
    data = load_data()
FileNotFoundError: No such file or directory: 'data/keypoints/hola.h5'
```

---

## 📋 Archivos Actualizados con Logging

### ✅ Archivos con logging implementado:

1. **`capture_samples.py`**
   - Log de inicio/fin de captura
   - Contador de muestras capturadas
   - Errores de cámara

2. **`normalize_samples.py`**
   - Progreso por palabra
   - Errores en normalización

3. **`create_keypoints.py`**
   - Progreso de extracción
   - Cantidad de muestras procesadas

4. **`main.py`**
   - Inicio de aplicación GUI
   - Errores de cámara y UI

5. **`training_model.py`** (ya tenía logging actualizado)
   - Progreso de entrenamiento
   - Métricas por época
   - Errores en datos

6. **`model.py`** (ya tenía logging actualizado)
   - Construcción del modelo
   - Configuración de capas

---

## 🐛 Debugging con Logs

### Ejemplo: Encontrar por qué falla el entrenamiento

```python
# 1. Habilitar modo DEBUG
from logger_config import set_log_level
set_log_level("DEBUG")

# 2. Ejecutar el script
python training_model.py

# 3. Ver logs detallados
# En consola:
#   DEBUG | Cargando keypoints de: data/keypoints/hola.h5
#   DEBUG | Secuencias cargadas: 30
#   DEBUG | Shape de X: (420, 15, 1662)
#   ERROR | No se encontró archivo: data/keypoints/adios.h5
```

### Ejemplo: Ver logs históricos

```powershell
# Ver log del día actual
Get-Content logs\lsp_20251014.log

# Buscar errores
Get-Content logs\lsp_20251014.log | Select-String "ERROR"

# Ver últimas 50 líneas
Get-Content logs\lsp_20251014.log -Tail 50
```

---

## 💡 Tips y Mejores Prácticas

### ✅ DO:

```python
# Usar logger del módulo
logger = get_logger(__name__)

# Mensajes descriptivos
logger.info("Procesando palabra 'hola': 30 muestras encontradas")

# Incluir contexto en errores
logger.error(f"Error procesando '{word_id}': {e}", exc_info=True)

# Usar emojis para claridad visual
logger.info("✓ Proceso completado")
logger.error("❌ Error crítico")
logger.warning("⚠️  Advertencia")
```

### ❌ DON'T:

```python
# No usar print()
print("Iniciando proceso...")  # ❌

# En su lugar:
logger.info("Iniciando proceso...")  # ✅

# No loggear en exceso
for i in range(10000):
    logger.debug(f"Iteración {i}")  # ❌ Genera archivos enormes

# Loggear cada N iteraciones:
for i in range(10000):
    if i % 1000 == 0:
        logger.debug(f"Progreso: {i}/10000")  # ✅
```

---

## 🔧 Solución de Problemas

### No veo logs en consola
```python
# Asegúrate de que console_output=True
from logger_config import setup_logging
setup_logging(console_output=True)
```

### Logs muy verbosos
```python
# Cambia a nivel INFO o WARNING
from logger_config import set_log_level
set_log_level("INFO")
```

### Archivo de log muy grande
- Los logs rotan automáticamente cada 10 MB
- Se mantienen 5 backups
- Puedes eliminar logs antiguos manualmente:
  ```powershell
  Remove-Item logs\*.log.* -Force
  ```

---

## 📖 Ejemplos Completos

### Ejemplo 1: Script simple con logging

```python
from logger_config import get_logger

logger = get_logger(__name__)

def procesar_datos():
    logger.info("Iniciando procesamiento de datos")
    
    try:
        # Tu código aquí
        datos = cargar_datos()
        logger.info(f"Datos cargados: {len(datos)} elementos")
        
        resultado = procesar(datos)
        logger.info("✓ Procesamiento completado")
        
        return resultado
        
    except FileNotFoundError as e:
        logger.error(f"❌ Archivo no encontrado: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("INICIANDO SCRIPT")
    logger.info("=" * 50)
    
    try:
        procesar_datos()
    except Exception:
        logger.critical("Script terminó con errores")
        exit(1)
    
    logger.info("✓ Script completado exitosamente")
```

### Ejemplo 2: Función con decoradores

```python
from logger_config import get_logger, log_function_call, log_execution_time

logger = get_logger(__name__)

@log_function_call
@log_execution_time
def entrenar_modelo(epochs=100):
    logger.info(f"Entrenando modelo por {epochs} épocas")
    
    for epoch in range(epochs):
        if epoch % 10 == 0:
            logger.info(f"Época {epoch}/{epochs}")
    
    logger.info("✓ Entrenamiento completado")
    return model
```

---

## 🎓 Resumen

**Logging agregado exitosamente al proyecto LSP:**

✅ Sistema centralizado en `logger_config.py`  
✅ Logs en consola con colores  
✅ Logs en archivo con rotación automática  
✅ Decoradores para funciones  
✅ Integrado en scripts principales  
✅ Facilita debugging y troubleshooting  

**Para usar:**
```python
from logger_config import get_logger
logger = get_logger(__name__)
logger.info("Tu mensaje aquí")
```

**Ver logs:**
```powershell
Get-Content logs\lsp_20251014.log
```

---

¡El proyecto ahora tiene logging profesional para facilitar el debugging! 🎉
