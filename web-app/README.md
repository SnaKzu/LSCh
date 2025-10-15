# 🌐 LSP Web Application

Aplicación web moderna para reconocimiento de Lengua de Señas Peruana en tiempo real.

![LSP Recognition](https://img.shields.io/badge/LSP-Recognition-blue)
![Python 3.10](https://img.shields.io/badge/Python-3.10-green)
![Flask](https://img.shields.io/badge/Flask-2.3.0-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API Endpoints](#api-endpoints)
- [WebSocket Events](#websocket-events)
- [Personalización](#personalización)
- [Troubleshooting](#troubleshooting)

---

## ✨ Características

### Frontend
- 🎨 **Diseño Moderno** con animaciones CSS fluidas
- 📱 **Responsive Design** compatible con móviles y tablets
- 🎥 **WebRTC** para captura de video en tiempo real
- 🔌 **WebSocket** para comunicación bidireccional instantánea
- 📊 **Estadísticas en Vivo** de predicciones y confianza
- 🎯 **UI/UX Intuitiva** con feedback visual inmediato

### Backend
- ⚡ **Flask + SocketIO** para servidor en tiempo real
- 🧠 **MediaPipe Integration** para detección de pose/manos/rostro
- 🤖 **Modelo LSTM** para clasificación de señas
- 📈 **API REST** para consultas de vocabulario y health check
- 🔄 **Gestión de Sesiones** múltiples usuarios simultáneos
- 📝 **Logging Completo** para debugging y monitoreo

---

## 📦 Requisitos

### Sistema
- Python 3.10.0
- Navegador moderno con soporte para:
  - WebRTC (getUserMedia)
  - WebSocket
  - HTML5 Canvas
  - ES6 JavaScript

### Dependencias Python
```
flask>=2.3.0
flask-cors>=4.0.0
flask-socketio>=5.3.0
python-socketio>=5.9.0
tensorflow>=2.15.0
mediapipe>=0.10.11
opencv-python>=4.8.0
numpy>=1.24.0
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
cd modelo_lstm_lsp-main
```

### 2. Instalar Dependencias
```powershell
# Instalar Flask y SocketIO
py -3.10 -m pip install flask flask-cors flask-socketio python-socketio --user

# Las demás dependencias ya deberían estar instaladas
# Si no, instalar desde requirements.txt
py -3.10 -m pip install -r requirements.txt --user
```

### 3. Verificar Modelo
Asegúrate de que el modelo entrenado existe:
```
models/actions_15.keras
models/words.json
```

### 4. Verificar Configuración
Revisa `config.yaml` para ajustar parámetros si es necesario.

---

## 🎯 Uso

### Iniciar el Servidor

#### Opción 1: Desde la carpeta backend
```powershell
cd web-app\backend
py -3.10 app.py
```

#### Opción 2: Desde la raíz del proyecto
```powershell
py -3.10 web-app\backend\app.py
```

El servidor iniciará en: **http://localhost:5000**

### Acceder a la Aplicación

1. **Página Principal**: http://localhost:5000/
   - Información del proyecto
   - Características
   - Vocabulario disponible
   - Stack tecnológico

2. **Demo Interactivo**: http://localhost:5000/demo
   - Activar cámara web
   - Reconocimiento en tiempo real
   - Historial de predicciones
   - Estadísticas de sesión

### Usar la Aplicación

1. **Abrir Demo**: Navega a http://localhost:5000/demo

2. **Activar Cámara**: 
   - Haz clic en "Activar Cámara"
   - Permite acceso a la webcam cuando el navegador lo solicite

3. **Realizar Señas**:
   - Posiciónate frente a la cámara
   - Asegúrate de que tu cuerpo y manos sean visibles
   - Realiza las señas del vocabulario LSP
   - La predicción aparecerá automáticamente

4. **Ver Resultados**:
   - Panel derecho muestra la predicción actual
   - Historial de últimas 10 señas reconocidas
   - Estadísticas de la sesión (precisión, tiempo, cantidad)

---

## 📁 Estructura del Proyecto

```
web-app/
├── backend/
│   ├── app.py              # Servidor Flask + SocketIO
│   └── uploads/            # Carpeta para archivos temporales
│
├── frontend/
│   ├── index.html          # Página principal
│   ├── demo.html           # Página de demo interactivo
│   │
│   ├── css/
│   │   ├── styles.css      # Estilos principales
│   │   └── demo.css        # Estilos específicos del demo
│   │
│   ├── js/
│   │   ├── app.js          # JavaScript página principal
│   │   └── demo.js         # JavaScript demo (WebRTC + WebSocket)
│   │
│   └── assets/
│       └── images/         # Imágenes y recursos
│
└── README.md              # Este archivo
```

---

## 🔌 API Endpoints

### GET `/`
**Descripción**: Página principal  
**Respuesta**: HTML de la landing page

### GET `/demo`
**Descripción**: Página de demo interactivo  
**Respuesta**: HTML del demo con WebRTC

### GET `/api/health`
**Descripción**: Health check del servidor  
**Respuesta JSON**:
```json
{
  "status": "ok",
  "model_loaded": true,
  "vocabulary_size": 14,
  "words": ["hola", "adios", ...]
}
```

### GET `/api/vocabulary`
**Descripción**: Obtener vocabulario completo  
**Respuesta JSON**:
```json
{
  "vocabulary": {
    "hola": "HOLA",
    "adios": "ADIÓS",
    ...
  },
  "total": 14
}
```

### POST `/api/predict-frame`
**Descripción**: Predecir desde un frame individual  
**Body**: 
```json
{
  "frame": "data:image/jpeg;base64,..."
}
```
**Respuesta**:
```json
{
  "has_hands": true,
  "keypoints_detected": {
    "pose": true,
    "face": true,
    "left_hand": true,
    "right_hand": false
  }
}
```

---

## 🔌 WebSocket Events

### Cliente → Servidor

#### `process_frame`
Enviar frame para procesamiento en tiempo real
```javascript
socket.emit('process_frame', {
  frame: 'data:image/jpeg;base64,...'
});
```

#### `clear_sentence`
Limpiar historial de predicciones
```javascript
socket.emit('clear_sentence');
```

#### `reset_session`
Reiniciar sesión completa
```javascript
socket.emit('reset_session');
```

### Servidor → Cliente

#### `connected`
Confirmación de conexión establecida
```javascript
socket.on('connected', (data) => {
  console.log(data.message);
});
```

#### `status`
Actualización del estado de procesamiento
```javascript
socket.on('status', (data) => {
  // data.recording: boolean
  // data.frame_count: number
  // data.has_hands: boolean
});
```

#### `prediction`
Nueva predicción disponible
```javascript
socket.on('prediction', (data) => {
  // data.word: string (ej: "HOLA")
  // data.word_id: string (ej: "hola")
  // data.confidence: number (ej: 0.92)
  // data.sentence: array (últimas 5 palabras)
});
```

#### `error`
Error durante el procesamiento
```javascript
socket.on('error', (data) => {
  console.error(data.message);
});
```

---

## 🎨 Personalización

### Colores y Tema

Edita `frontend/css/styles.css` en la sección de variables CSS:

```css
:root {
    --primary: #6366f1;           /* Color primario */
    --secondary: #f59e0b;         /* Color secundario */
    --success: #10b981;           /* Color de éxito */
    --danger: #ef4444;            /* Color de error */
    
    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
```

### Configuración del Servidor

Edita `backend/app.py`:

```python
# Cambiar host y puerto
socketio.run(app, 
             host='0.0.0.0',    # Cambiar a tu host
             port=5000,          # Cambiar puerto
             debug=True)         # False para producción
```

### Umbral de Confianza

Edita `config.yaml`:

```yaml
evaluation:
  confidence_threshold: 0.8  # Cambiar umbral (0.0 a 1.0)
```

---

## 🔧 Troubleshooting

### Problema: Servidor no inicia

**Error**: `ModuleNotFoundError: No module named 'flask_socketio'`

**Solución**:
```powershell
py -3.10 -m pip install flask-socketio python-socketio --user
```

---

### Problema: Modelo no se carga

**Error**: `FileNotFoundError: models/actions_15.keras`

**Solución**:
Asegúrate de que el modelo existe en la ruta correcta:
```powershell
ls models/
# Debe mostrar: actions_15.keras, words.json
```

---

### Problema: Cámara no se activa

**Error**: `NotAllowedError: Permission denied`

**Solución**:
1. Verifica permisos del navegador para acceder a la cámara
2. Usa HTTPS en producción (WebRTC requiere conexión segura)
3. Comprueba que no hay otra app usando la cámara

---

### Problema: WebSocket no conecta

**Error**: `Socket.IO connection failed`

**Solución**:
1. Verifica que el servidor esté corriendo: http://localhost:5000
2. Comprueba la consola del navegador (F12) para errores
3. Verifica que el puerto 5000 no esté bloqueado por firewall
4. Prueba desactivar extensiones del navegador (ej: AdBlock)

---

### Problema: Predicciones lentas

**Síntomas**: Delay > 1 segundo entre frames

**Solución**:
1. Reduce la resolución de la cámara en `demo.js`:
```javascript
video: {
    width: { ideal: 640 },   // Reducir de 1280
    height: { ideal: 480 }   // Reducir de 720
}
```

2. Aumenta el intervalo de procesamiento:
```javascript
setTimeout(() => this.processFrames(), 50);  // De 33ms a 50ms
```

---

### Problema: Errores de CORS

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solución**:
Ya está configurado CORS en `app.py`. Si persiste:
```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

---

## 📊 Métricas de Performance

### Backend
- **Procesamiento por Frame**: ~30-50ms
- **Latencia WebSocket**: ~10-20ms
- **Memoria RAM**: ~500MB (modelo + MediaPipe)
- **CPU**: 15-25% (procesamiento continuo)

### Frontend
- **FPS de Video**: 30 fps
- **Carga Inicial**: ~2s
- **Bundle Size**: 
  - HTML: 15 KB
  - CSS: 25 KB
  - JS: 18 KB

---

## 🔐 Consideraciones de Seguridad

### Producción

1. **Deshabilitar Debug Mode**:
```python
socketio.run(app, debug=False)
```

2. **Usar HTTPS**:
```python
socketio.run(app, ssl_context='adhoc')  # Certificado temporal
# O usar certificados reales
```

3. **Limitar Tamaño de Uploads**:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

4. **Validar Inputs**:
```python
from werkzeug.utils import secure_filename
filename = secure_filename(file.filename)
```

5. **Rate Limiting**:
```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["100 per hour"])
```

---

## 📝 Licencia

MIT License - Ver archivo `LICENSE` para más detalles

---

## 👥 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 📞 Soporte

¿Problemas o preguntas?

- 📧 Email: contact@lsp-project.com
- 💬 GitHub Issues: [Crear Issue](https://github.com/tu-usuario/lsp-project/issues)
- 📖 Documentación: Ver archivos en `/docs`

---

## 🎉 Agradecimientos

- MediaPipe por la detección de pose/manos
- TensorFlow por el framework de Deep Learning
- Flask y SocketIO por el backend en tiempo real
- Comunidad sorda peruana por el apoyo en LSP

---

**¡Hecho con ❤️ para la comunidad sorda peruana!**
