# 🚀 GUÍA DE MIGRACIÓN - TensorFlow 2.15+ y Configuración Centralizada

## 📋 Resumen de Cambios

Este proyecto ha sido refactorizado para:
- ✅ **Actualizar a TensorFlow 2.15.0** (desde 2.10.1)
- ✅ **Centralizar configuración en `config.yaml`**
- ✅ **Mejorar mantenibilidad y escalabilidad**
- ✅ **Agregar logging y manejo de errores**

---

## 🔄 Cambios Principales

### 1. Nuevo Sistema de Configuración

**ANTES:**
```python
# constants.py (múltiples archivos)
from constants import MODEL_PATH, MODEL_FRAMES, words_text
```

**AHORA:**
```python
# config_manager.py (centralizado)
from config_manager import config

model_path = config.get_model_path()
model_frames = config.model.frames
word_label = config.get_word_label("hola")
```

### 2. TensorFlow 2.15+ (sin `keras` separado)

**ANTES:**
```python
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.utils import to_categorical
```

**AHORA:**
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical
```

### 3. Actualización de Dependencias

| Paquete | Versión Anterior | Versión Nueva |
|---------|------------------|---------------|
| TensorFlow | 2.10.1 | 2.15.0 |
| Keras | 2.10.0 (separado) | Incluido en TF |
| OpenCV | 4.9.0.80 | 4.10.0.84 |
| PyQt5 | 5.15.9 | 5.15.11 |
| gTTS | 2.5.1 | 2.5.3 |
| protobuf | <4.0 | 4.25.3 |

---

## 📦 Instalación y Actualización

### Paso 1: Verificar Python

Este proyecto ahora requiere **Python 3.10, 3.11, o 3.12**:

```powershell
python --version
# Debe mostrar: Python 3.10.x, 3.11.x o 3.12.x
```

Si tienes Python 3.7-3.9, necesitas actualizar Python.

### Paso 2: Crear Entorno Virtual (Recomendado)

```powershell
# Navega al proyecto
cd C:\Users\Diego\Documents\test6\modelo_lstm_lsp-main

# Crea entorno virtual
python -m venv venv

# Activa el entorno
.\venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecuta:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 3: Instalar Dependencias Actualizadas

```powershell
# Desinstala versiones antiguas (opcional pero recomendado)
pip uninstall tensorflow keras -y

# Instala nuevas dependencias
pip install -r requirements.txt

# Verifica la instalación
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
```

**Salida esperada:**
```
TensorFlow: 2.15.0
```

### Paso 4: Instalar PyYAML (para config.yaml)

```powershell
pip install PyYAML==6.0.2
```

---

## 🔧 Migración de Código Existente

### Opción 1: Sin Cambios (Backward Compatible)

El código legacy sigue funcionando gracias a `constants.py`:

```python
# Tu código antiguo sigue funcionando
from constants import MODEL_PATH, MODEL_FRAMES, words_text

# No necesitas cambiar nada
```

⚠️ **Pero verás un warning:**
```
DeprecationWarning: constants.py está deprecado. Use 'from config_manager import config'
```

### Opción 2: Migrar a Config Centralizado (Recomendado)

#### Ejemplo 1: Importaciones

```python
# ❌ Antiguo
from constants import MODEL_PATH, MODEL_FRAMES, KEYPOINTS_PATH, words_text

# ✅ Nuevo
from config_manager import config

model_path = config.get_model_path()
model_frames = config.model.frames
keypoints_path = config.get_keypoints_path()
word_label = config.get_word_label("buenos_dias")  # "BUENOS DÍAS"
```

#### Ejemplo 2: Usar Paths

```python
# ❌ Antiguo
import os
word_path = os.path.join(FRAME_ACTIONS_PATH, word_id)

# ✅ Nuevo
word_path = config.get_frame_actions_path(word_id)
```

#### Ejemplo 3: Acceder a Configuración

```python
# ✅ Nuevo - Acceso a cualquier configuración
confidence_threshold = config.evaluation.confidence_threshold  # 0.8
batch_size = config.training.batch_size  # 8
epochs = config.training.epochs  # 500
lstm_units = config.network.lstm1_units  # 64
```

---

## 📝 Cambios por Archivo

### `model.py`

**Cambios:**
- ✅ Importa de `tensorflow.keras` en lugar de `keras`
- ✅ Lee configuración de red desde `config.yaml`
- ✅ Agrega logging
- ✅ Mejora documentación

**Acción requerida:** Ninguna (compatible con código existente)

### `training_model.py`

**Cambios:**
- ✅ Usa `tensorflow.keras` en lugar de `keras`
- ✅ Agrega callbacks mejorados (ModelCheckpoint, ReduceLROnPlateau)
- ✅ Mejor logging de progreso
- ✅ Usa float32 en lugar de float16 para mejor precisión

**Acción requerida:**  
Si personalizaste este archivo, revisa los nuevos parámetros en `config.yaml`:

```yaml
training:
  epochs: 500
  batch_size: 8
  validation_split: 0.05
  early_stopping_patience: 10
```

### `constants.py`

**Cambios:**
- ⚠️ Ahora es un wrapper de `config_manager.py`
- ✅ Mantiene retrocompatibilidad
- ✅ Emite warnings para fomentar migración

**Acción requerida:** Considera migrar a `config_manager`.

### `helpers.py`

**Cambios:**
- ✅ Mejor documentación con type hints
- ✅ Usa `config_manager` internamente
- ✅ Agrega logging
- ✅ Mejor manejo de errores

**Acción requerida:** Ninguna (API sin cambios)

---

## 🆕 Nuevo Archivo: `config.yaml`

Toda la configuración ahora está centralizada aquí. Para modificar el proyecto:

### Cambiar Número de Frames

```yaml
model:
  frames: 20  # Cambiar de 15 a 20
```

Luego, reentrenar el modelo.

### Agregar Nueva Palabra

```yaml
vocabulary:
  word_ids:
    - "adios"
    - "bien"
    - "tu_nueva_palabra"  # ← Agregar aquí
  
  word_labels:
    tu_nueva_palabra: "TU NUEVA PALABRA"  # ← Y aquí
```

### Ajustar Hiperparámetros

```yaml
network:
  lstm1_units: 128  # Aumentar de 64 a 128
  lstm2_units: 256  # Aumentar de 128 a 256
  
training:
  batch_size: 16  # Aumentar de 8 a 16
  epochs: 1000  # Aumentar de 500 a 1000
```

---

## 🧪 Verificar la Migración

### Test 1: Importar ConfigManager

```powershell
python -c "from config_manager import config; print('✓ Config cargado')"
```

### Test 2: Verificar TensorFlow

```powershell
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"
```

### Test 3: Construir Modelo

```powershell
python model.py
```

**Salida esperada:**
```
==================== ARQUITECTURA DEL MODELO LSTM
...
✓ Modelo compatible con TensorFlow 2.15.0
```

### Test 4: Ejecutar Training (dry-run)

```powershell
# Solo valida, no entrena (ctrl+C después de ver el progreso)
python training_model.py
```

---

## 🐛 Solución de Problemas Comunes

### Error: "No module named 'keras'"

**Causa:** Código antiguo importa `keras` directamente.

**Solución:**
```python
# Cambiar
from keras.models import Sequential

# Por
from tensorflow.keras.models import Sequential
```

### Error: "FileNotFoundError: config.yaml"

**Causa:** No estás ejecutando desde el directorio del proyecto.

**Solución:**
```powershell
cd C:\Users\Diego\Documents\test6\modelo_lstm_lsp-main
python tu_script.py
```

### Error: "ModuleNotFoundError: No module named 'yaml'"

**Solución:**
```powershell
pip install PyYAML
```

### Warning: "DeprecationWarning: constants.py está deprecado"

**Causa:** Estás usando el sistema antiguo (funciona pero no es recomendado).

**Solución:** Migra a `config_manager` (ver sección "Migración de Código").

### Error al cargar modelo antiguo (.keras)

**Causa:** El modelo fue entrenado con TensorFlow 2.10.

**Solución:**
```powershell
# Reentrenar con TensorFlow 2.15
python training_model.py
```

Los modelos son **mayormente compatibles**, pero para óptimo rendimiento, reentrenar es recomendado.

---

## 📊 Ventajas del Nuevo Sistema

### ✅ Configuración Centralizada

- Un solo archivo (`config.yaml`) en lugar de múltiples constantes
- Fácil de modificar sin tocar código
- Validación automática de configuración

### ✅ TensorFlow 2.15+

- Mejor rendimiento y optimizaciones
- Soporte para hardware más nuevo
- Correcciones de seguridad
- APIs más modernas

### ✅ Mejor Código

- Type hints para autocompletado
- Logging profesional
- Documentación mejorada
- Manejo de errores robusto

### ✅ Escalabilidad

- Fácil agregar nuevas palabras
- Fácil ajustar hiperparámetros
- Fácil experimentar con diferentes configuraciones

---

## 🚀 Próximos Pasos

1. **Reentrena tu modelo** con TensorFlow 2.15:
   ```powershell
   python training_model.py
   ```

2. **Prueba el nuevo modelo**:
   ```powershell
   python evaluate_model.py
   ```

3. **Migra tu código personalizado** a usar `config_manager`

4. **Experimenta con el nuevo sistema**:
   - Modifica `config.yaml` para probar diferentes configuraciones
   - Agrega nuevas palabras fácilmente
   - Ajusta hiperparámetros sin tocar código

---

## 📞 Soporte

Si encuentras problemas:

1. Verifica que tienes Python 3.10+
2. Verifica que instalaste todas las dependencias
3. Revisa los logs (ahora hay logging detallado)
4. Consulta esta guía de migración

---

## 📌 Resumen de Comandos

```powershell
# Setup inicial
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Verificar instalación
python -c "from config_manager import config; print('✓ OK')"
python -c "import tensorflow as tf; print(tf.__version__)"

# Workflow completo
python capture_samples.py      # Capturar datos
python normalize_samples.py    # Normalizar
python create_keypoints.py     # Extraer keypoints
python training_model.py       # Entrenar (con TF 2.15!)
python evaluate_model.py       # Evaluar

# GUI
python main.py
```

---

**¡Felicidades! Tu proyecto ahora está actualizado y refactorizado. 🎉**
