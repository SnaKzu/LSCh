# 🤟 Traductor de Lengua de Señas Peruana (LSP) a Texto y Voz

Sistema de reconocimiento en tiempo real de Lengua de Señas Peruana usando **LSTM + MediaPipe**. Detecta señas mediante cámara, las traduce a texto español y genera síntesis de voz.

[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-orange)](https://tensorflow.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.11-green)](https://mediapipe.dev)

---

## 🎯 Características

- ✅ **Detección en tiempo real** de 14 palabras en LSP
- ✅ **Interfaz gráfica** con PyQt5
- ✅ **Síntesis de voz** automática (Text-to-Speech)
- ✅ **API REST** con Flask para integración
- ✅ **Configuración centralizada** en YAML
- ✅ **Pipeline completo**: Captura → Entrenamiento → Inferencia

---

## 📋 Vocabulario (14 palabras)

```
Saludos:     hola, buenos días, buenas tardes, buenas noches, adiós
Estados:     bien, mal, más o menos
Cortesía:    gracias, por favor, disculpa, me ayudas
Preguntas:   cómo estás
```

---

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```powershell
# Clonar o descargar el proyecto
cd modelo_lstm_lsp-main

# Ejecutar script de setup
.\setup.ps1
```

### Opción 2: Manual

```powershell
# 1. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 3. Verificar instalación
python -c "from config_manager import config; print('✓ OK')"
```

---

## 📚 Uso del Sistema

### 1️⃣ Usar Modelo Preentrenado (Más Rápido)

```powershell
# Interfaz gráfica
python main.py

# Modo consola (sin GUI)
python evaluate_model.py
```

### 2️⃣ Entrenar Tu Propio Modelo (Completo)

```powershell
# Paso 1: Capturar muestras (30-50 por palabra)
python capture_samples.py

# Paso 2: Normalizar frames a 15 por muestra
python normalize_samples.py

# Paso 3: Extraer keypoints (1662 valores por frame)
python create_keypoints.py

# Paso 4: Entrenar red LSTM
python training_model.py

# Paso 5: Evaluar resultados
python evaluate_model.py
```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│          ENTRADA: Video (Cámara)            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      MediaPipe Holistic (Google)            │
│  Detecta: Pose (33) + Cara (468) +          │
│          Manos (21+21) = 1662 keypoints     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Normalización a 15 frames              │
│  Interpola/Submuestrea secuencias           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│       Red Neuronal LSTM                     │
│  LSTM(64) → LSTM(128) → Dense → Softmax     │
│  Input: (15, 1662) → Output: (14 clases)   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      SALIDA: Texto + Voz (gTTS)             │
│  Ej: "BUENOS DÍAS" + audio.mp3              │
└─────────────────────────────────────────────┘
```

---

## ⚙️ Configuración

Toda la configuración está centralizada en **`config.yaml`**:

```yaml
# Parámetros del modelo
model:
  frames: 15              # Frames por secuencia
  keypoints_length: 1662  # Dimensión del vector
  min_length_frames: 5    # Mínimo para validar seña

# Hiperparámetros de entrenamiento
training:
  epochs: 500
  batch_size: 8
  validation_split: 0.05
  early_stopping_patience: 10

# Arquitectura de red
network:
  lstm1_units: 64
  lstm2_units: 128
  dropout: 0.5

# Vocabulario
vocabulary:
  word_ids: [adios, bien, buenos_dias, ...]
  word_labels:
    buenos_dias: "BUENOS DÍAS"
```

Para modificar, edita `config.yaml` y reent rena el modelo.

---

## 📁 Estructura del Proyecto

```
modelo_lstm_lsp-main/
├── config.yaml              # ⚙️ Configuración central
├── config_manager.py        # 📦 Gestor de configuración
├── requirements.txt         # 📋 Dependencias
├── setup.ps1                # 🚀 Script de instalación
├── MIGRATION_GUIDE.md       # 📖 Guía de migración
│
├── model.py                 # 🧠 Arquitectura LSTM
├── training_model.py        # 🎓 Entrenamiento
├── evaluate_model.py        # 🧪 Evaluación
├── main.py                  # 🖥️ Interfaz gráfica
│
├── capture_samples.py       # 📹 Captura de datos
├── normalize_samples.py     # ⚖️ Normalización
├── create_keypoints.py      # 🔑 Extracción keypoints
│
├── helpers.py               # 🛠️ Utilidades
├── constants.py             # 📌 Constantes (legacy)
├── text_to_speech.py        # 🔊 Síntesis de voz
├── server.py                # 🌐 API REST
│
├── models/                  # 💾 Modelos entrenados
│   ├── actions_15.keras
│   └── words.json
│
├── data/                    # 📊 Datos procesados
│   └── keypoints/
│
└── frame_actions/           # 🎬 Muestras de video
    ├── hola/
    ├── buenos_dias/
    └── ...
```

---

## 🔧 Agregar Nueva Palabra

### 1. Editar `config.yaml`

```yaml
vocabulary:
  word_ids:
    - "adios"
    - "bien"
    - "tu_nueva_palabra"  # ← Agregar aquí
  
  word_labels:
    tu_nueva_palabra: "TU NUEVA PALABRA"
```

### 2. Capturar Muestras

```python
# En capture_samples.py, línea final:
word_name = "tu_nueva_palabra"
word_path = os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH, word_name)
capture_samples(word_path)
```

Ejecutar: `python capture_samples.py` (grabar 30-50 muestras)

### 3. Procesar y Entrenar

```powershell
python normalize_samples.py
python create_keypoints.py
python training_model.py
```

---

## 🌐 API REST

Iniciar servidor:

```powershell
python server.py
```

Endpoint disponible:

```bash
POST http://localhost:5000/upload_video
Content-Type: multipart/form-data

{
  "video": <archivo_video>
}

# Respuesta:
"HOLA - BUENOS DÍAS - GRACIAS"
```

---

## 📊 Métricas y Evaluación

```python
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Generar matriz de confusión
python confusion_matrix.py

# Ver historial de entrenamiento
# Automático en training_model.py
```

---

## 🐛 Solución de Problemas

### Error: `ModuleNotFoundError: No module named 'yaml'`
```powershell
pip install PyYAML
```

### Error: `cannot import name 'builder' from 'google.protobuf'`
```powershell
pip install protobuf==3.20.3 --force-reinstall
```

### Error: MediaPipe no funciona en Python 3.12
```powershell
# Usar Python 3.10 o 3.11
python3.10 -m venv venv
```

### Error al cargar modelo `.keras`
```powershell
# Reentrenar con TensorFlow actual
python training_model.py
```

Más soluciones en **`MIGRATION_GUIDE.md`**

---

## 📖 Documentación

- **`MIGRATION_GUIDE.md`** - Guía de migración a TensorFlow 2.15+
- **`config.yaml`** - Configuración con comentarios
- **Código fuente** - Docstrings completos en cada función

---

## 🎓 Tecnologías Utilizadas

| Tecnología | Propósito |
|------------|-----------|
| **TensorFlow/Keras** | Red neuronal LSTM |
| **MediaPipe** | Detección de pose y manos |
| **OpenCV** | Procesamiento de video |
| **PyQt5** | Interfaz gráfica |
| **Flask** | API REST |
| **gTTS + pygame** | Síntesis de voz |
| **NumPy/Pandas** | Manejo de datos |
| **PyYAML** | Configuración |

---

## 📝 Requisitos del Sistema

- **Python:** 3.10, 3.11 o 3.12
- **RAM:** Mínimo 4GB (8GB recomendado)
- **GPU:** Opcional (acelera entrenamiento)
- **Cámara:** Para captura y evaluación en tiempo real
- **Espacio:** ~2GB (dependencias + datos)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-palabra`
3. Commit cambios: `git commit -m 'Agrega palabra X'`
4. Push: `git push origin feature/nueva-palabra`
5. Abre un Pull Request

---

## 📹 Video Tutorial

[Video explicativo del código](https://youtu.be/3EK0TxfoAMk)

---

## 📜 Licencia

Este proyecto es de código abierto para fines educativos y de investigación.

---

## 👨‍💻 Autor

Proyecto de reconocimiento de Lengua de Señas Peruana usando Deep Learning

---

## 🆕 Changelog

### v2.0 (Octubre 2025)
- ✅ Actualizado a TensorFlow 2.15.0
- ✅ Configuración centralizada con YAML
- ✅ Mejor arquitectura de código
- ✅ Script de instalación automática
- ✅ Documentación mejorada

### v1.0 (Inicial)
- ✅ Implementación básica con TensorFlow 2.10
- ✅ 14 palabras en LSP
- ✅ Interfaz gráfica PyQt5

---

**¡Felicidades! Ahora tienes un sistema completo de reconocimiento de LSP. 🎉**

Para comenzar, ejecuta: `.\setup.ps1`
