# 🔧 Solución: Error de Versión de Python

## ❌ Problema Actual

Estás usando **Python 3.13** pero el proyecto requiere **Python 3.10, 3.11 o 3.12**.

```
Traceback (most recent call last):
  File "main.py", line 2, in <module>
    import cv2
```

**Causa:** MediaPipe no es compatible con Python 3.13.

---

## ✅ Solución Rápida (3 minutos)

### Opción 1: Usar Python 3.10 con py launcher (RECOMENDADO)

```powershell
# 1. Navegar al proyecto
cd C:\Users\Diego\Documents\test6\modelo_lstm_lsp-main

# 2. Crear entorno virtual con Python 3.10
py -3.10 -m venv venv

# 3. Activar el entorno
.\venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 5. Ejecutar el proyecto
python main.py
```

### Opción 2: Usar Python 3.11

```powershell
cd C:\Users\Diego\Documents\test6\modelo_lstm_lsp-main
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

---

## 🎯 Configurar VS Code

### 1. Seleccionar el Intérprete Correcto

1. Presiona `Ctrl + Shift + P`
2. Escribe: `Python: Select Interpreter`
3. Selecciona: `.\venv\Scripts\python.exe` (el que acabas de crear)

### 2. Verificar la Versión

```powershell
python --version
# Debe mostrar: Python 3.10.0 o Python 3.11.0
```

---

## 📋 Pasos Completos Detallados

### 1. Crear Entorno Virtual

```powershell
# Opción A: Con Python 3.10 (RECOMENDADO)
py -3.10 -m venv venv

# Opción B: Con Python 3.11
py -3.11 -m venv venv
```

### 2. Activar el Entorno

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Si da error de ejecución de scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### 4. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

Si hay problemas con protobuf:
```powershell
pip install protobuf==3.20.3 --force-reinstall
```

### 5. Verificar Instalación

```powershell
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"
python -c "import mediapipe as mp; print('MediaPipe OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### 6. Ejecutar el Proyecto

```powershell
python main.py
```

---

## 🐛 Solución de Problemas

### Error: "cannot import name 'builder' from 'google.protobuf'"

```powershell
pip install protobuf==3.20.3 --force-reinstall
```

### Error: "No module named 'cv2'"

```powershell
pip install opencv-contrib-python==4.10.0.84
```

### Error: "DLL load failed" (MediaPipe en Windows)

```powershell
# Reinstalar con versión específica
pip uninstall mediapipe
pip install mediapipe==0.10.11
```

### Error: "Execution Policy" al activar venv

```powershell
# Permitir scripts en PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego activar de nuevo
.\venv\Scripts\Activate.ps1
```

### Error: "pip no se encuentra"

```powershell
# Usar python -m pip en lugar de pip
python -m pip install -r requirements.txt
```

---

## 🔍 Verificar Todo Funciona

### Script de Verificación Completo

```powershell
# 1. Verificar versión de Python
python --version

# 2. Verificar todas las dependencias
python -c "
import sys
print(f'Python {sys.version}')
import tensorflow as tf
print(f'✓ TensorFlow {tf.__version__}')
import mediapipe as mp
print('✓ MediaPipe OK')
import cv2
print(f'✓ OpenCV {cv2.__version__}')
from PyQt5.QtWidgets import QApplication
print('✓ PyQt5 OK')
import numpy as np
print(f'✓ NumPy {np.__version__}')
print('\n✅ Todas las dependencias instaladas correctamente')
"

# 3. Verificar configuración del proyecto
python -c "
from config_manager import config
print(f'✓ Configuración cargada')
print(f'✓ {len(config.get_word_ids())} palabras configuradas')
"

# 4. Verificar helpers
python -c "
from helpers import mediapipe_detection, extract_keypoints
print('✓ helpers.py OK')
"
```

---

## 📦 Instalación Alternativa con setup.ps1

Si prefieres instalación automática:

```powershell
# 1. Asegúrate de estar en el directorio correcto
cd C:\Users\Diego\Documents\test6\modelo_lstm_lsp-main

# 2. Ejecuta el script de instalación
.\setup.ps1

# Sigue las instrucciones en pantalla
# El script detectará automáticamente Python 3.10 o 3.11
```

---

## 🎓 Comandos Útiles

### Activar/Desactivar Entorno Virtual

```powershell
# Activar
.\venv\Scripts\Activate.ps1

# Desactivar
deactivate
```

### Ver Paquetes Instalados

```powershell
pip list
```

### Actualizar un Paquete

```powershell
pip install --upgrade nombre_paquete
```

### Reinstalar Todo

```powershell
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## 📊 Resumen de Versiones Compatibles

| Software | Versión Compatible | Tu Sistema |
|----------|-------------------|------------|
| Python | 3.10, 3.11, 3.12 | ✅ 3.10.0, 3.11.0 |
| TensorFlow | 2.15.0 | ✅ (se instalará) |
| MediaPipe | 0.10.11 | ✅ (se instalará) |
| OpenCV | 4.10.0.84 | ✅ (se instalará) |
| PyQt5 | 5.15.11 | ✅ (se instalará) |

---

## ✅ Checklist Final

Antes de ejecutar `main.py`:

- [ ] Entorno virtual creado con Python 3.10 o 3.11
- [ ] Entorno virtual activado (ves `(venv)` en el prompt)
- [ ] `pip` actualizado
- [ ] Todas las dependencias instaladas sin errores
- [ ] Verificación exitosa de imports
- [ ] VS Code usando el intérprete correcto

---

## 🚀 Ejecutar el Proyecto

Una vez todo configurado:

```powershell
# Asegúrate de que el entorno virtual esté activado
python main.py
```

**Debería abrir la GUI y comenzar a capturar video de la cámara.**

---

## 📞 Más Ayuda

- **README_UPDATED.md** - Documentación completa del proyecto
- **MIGRATION_GUIDE.md** - Guía de migración y troubleshooting
- **QUICKSTART.md** - Inicio rápido

---

**¡Listo! Ahora puedes usar el proyecto con la versión correcta de Python.** 🎉
