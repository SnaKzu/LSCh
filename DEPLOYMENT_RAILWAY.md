# 🚀 Despliegue en Railway - LSCh Recognition

## Preparación del Proyecto

### 1. Crear archivos de configuración

#### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### `Procfile`
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

#### Actualizar `requirements.txt`
```txt
# Core
Flask==3.0.3
Flask-CORS==4.0.0
Flask-SocketIO==5.5.1
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
gunicorn==21.2.0
eventlet==0.35.2

# ML/AI
tensorflow==2.15.0
mediapipe==0.10.11
opencv-python-headless==4.10.0.84
numpy==1.26.4
pandas==2.2.2
scikit-learn==1.4.2

# Utils
python-dotenv==1.0.1
Werkzeug==3.0.3
psycopg2-binary==2.9.9

# Production
whitenoise==6.6.0
```

### 2. Configurar variables de entorno

#### `.env` (no subir a Git)
```env
# Producción
FLASK_ENV=production
SECRET_KEY=tu-clave-super-secreta-aqui-cambiar
DATABASE_URL=postgresql://...  # Railway lo genera automáticamente

# ML Model
MODEL_PATH=models/actions_15.keras
WORDS_JSON_PATH=models/words.json

# Configuración
DEBUG=False
CONFIDENCE_THRESHOLD=0.7
```

### 3. Modificar `app.py` para producción

```python
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración dinámica
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///lsp_users.db')

# Para PostgreSQL en Railway
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')

# Configuración para producción
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
```

## Pasos de Despliegue

### 1. Preparar repositorio GitHub
```bash
# Si no tienes git inicializado
git init
git add .
git commit -m "Initial commit - LSCh Recognition App"

# Crear repo en GitHub y conectar
git remote add origin https://github.com/tu-usuario/lsch-recognition.git
git push -u origin main
```

### 2. Desplegar en Railway

1. **Registro**: Ve a [railway.app](https://railway.app) y regístrate con GitHub
2. **Nuevo Proyecto**: Click "New Project" → "Deploy from GitHub repo"
3. **Seleccionar Repo**: Conecta tu repositorio de LSCh Recognition
4. **Variables de Entorno**: 
   ```
   SECRET_KEY=tu-clave-secreta-aqui
   FLASK_ENV=production
   CONFIDENCE_THRESHOLD=0.7
   ```
5. **Base de Datos**: Click "Add Database" → "PostgreSQL"
6. **Deploy**: Railway automáticamente detecta Python y despliega

### 3. Configurar dominio personalizado (Opcional)
```
1. Settings → Domains
2. Generate Domain (obtienes algo como: lsch-recognition.up.railway.app)
3. O conectar tu dominio personalizado
```

## Estructura Final
```
proyecto/
├── web-app/
│   ├── backend/
│   │   ├── app.py
│   │   ├── models.py
│   │   └── requirements.txt
│   └── frontend/
├── models/
│   ├── actions_15.keras
│   └── words.json
├── railway.json
├── Procfile
├── .env
├── .gitignore
└── README.md
```

## Costos Railway
- **Starter**: $0/mes (500 horas gratis)
- **Hobby**: $5/mes (unlimited)
- **Pro**: $20/mes (features avanzadas)

## Comandos útiles
```bash
# Ver logs en tiempo real
railway logs --tail

# Ejecutar comandos en el servidor
railway shell

# Variables de entorno
railway variables
```

## Ventajas Railway
✅ Deploy automático en cada push  
✅ SSL/HTTPS automático  
✅ Escalamiento automático  
✅ Base de datos PostgreSQL incluida  
✅ Logs y métricas  
✅ Rollback fácil  
✅ Configuración mínima  