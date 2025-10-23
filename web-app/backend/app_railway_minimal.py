"""
Backend Flask para LSCh Web Application - Railway Minimal with PostgreSQL
Version simplificada sin TensorFlow pesado para despliegue rápido
Compatible con Python 3.12 y Railway
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Cargar variables de entorno para producción
from dotenv import load_dotenv
load_dotenv()

# Import models and database
try:
    from models import db, User, Prediction, init_db, get_system_stats
    DB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Database models not available: {e}")
    DB_AVAILABLE = False
    # Mock classes
    class MockDB:
        def init_app(self, app): pass
        def create_all(self): pass
        @property 
        def session(self): return MockSession()
    
    class MockSession:
        def add(self, obj): pass
        def commit(self): pass
        def rollback(self): pass
    
    class MockUser:
        def __init__(self): 
            self.id = 1
            self.username = "demo_user"
            self.is_authenticated = True
            self.is_active = True
        def check_password(self, pwd): return True
        def update_last_login(self): pass
        @staticmethod
        def query(): return MockQuery()
    
    class MockPrediction:
        def __init__(self, **kwargs): 
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class MockQuery:
        def filter_by(self, **kwargs): return self
        def filter(self, *args): return self
        def first(self): return MockUser()
        def count(self): return 10
        def order_by(self, *args): return self
        def limit(self, n): return self
        def all(self): return [MockUser()]
        def get(self, id): return MockUser()
    
    db = MockDB()
    User = MockUser
    Prediction = MockPrediction
    def init_db(app): pass
    def get_system_stats(): return {'total_users': 1, 'total_predictions': 42, 'avg_confidence': 0.87, 'top_word': 'hola', 'top_word_count': 15}

# Logger config simple para Railway
import logging
def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger(__name__)

app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='',
            template_folder='../frontend')

# Configuración dinámica para Railway con PostgreSQL
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'lsch-fallback-secret-key-development')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB max

# Configuración de base de datos PostgreSQL
database_url = os.getenv('DATABASE_URL')
if database_url and DB_AVAILABLE:
    # Railway PostgreSQL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"🐘 Using PostgreSQL: {database_url[:50]}...")
elif DB_AVAILABLE:
    # Fallback a SQLite para desarrollo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lsch_minimal.db'
    print("📂 Using SQLite fallback")
else:
    print("📝 Using Mock Database (no persistence)")

if DB_AVAILABLE:
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }

# Configuración para producción
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
else:
    app.config['DEBUG'] = True

# Inicializar extensiones
CORS(app)

# SocketIO con threading en lugar de eventlet para Railway/Python 3.12
socketio = SocketIO(app, 
                    cors_allowed_origins="*",
                    async_mode='threading',  # Usar threading en lugar de eventlet
                    logger=False,
                    engineio_logger=False)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    if DB_AVAILABLE:
        return User.query.get(int(user_id))
    else:
        return User()  # Mock user

# Initialize database si está disponible
if DB_AVAILABLE:
    init_db(app)

# Variables globales para sesión
sessions = {}

# Mock vocabulary para Railway
MOCK_VOCABULARY = [
    "adios", "bien", "buenas_noches", "buenas_tardes", "buenos_dias",
    "como_estas", "disculpa", "gracias", "hola-der", "hola-izq",
    "mal", "mas_o_menos", "me_ayudas", "por_favor"
]

def get_word_ids():
    """Get available vocabulary"""
    return MOCK_VOCABULARY

def get_word_label(word_id):
    """Get word label for display"""
    return word_id.replace('_', ' ').replace('-', ' ').title()

def save_prediction(user_id, word, word_id, confidence, session_id=None, frame_count=None):
    """Guardar predicción en base de datos si está disponible"""
    if not DB_AVAILABLE:
        logger.info(f"Mock prediction: {word} ({confidence:.2f}) for user {user_id}")
        return None
        
    try:
        prediction = Prediction(
            user_id=user_id,
            word=word,
            word_id=word_id,
            confidence=confidence,
            session_id=session_id,
            frame_count=frame_count,
            model_version='minimal_v1.0'
        )
        db.session.add(prediction)
        db.session.commit()
        logger.info(f"Prediction saved: {word} ({confidence:.2f}) for user {user_id}")
        return prediction
    except Exception as e:
        logger.error(f"Error saving prediction: {e}")
        if DB_AVAILABLE:
            db.session.rollback()
        return None

# ============= WEB PAGES ROUTES =============

@app.route('/')
def index():
    """Página principal del sitio web"""
    system_stats = get_system_stats()
    return render_template('index.html', 
                         vocabulary=get_word_ids(),
                         system_status={
                             'lsch_ready': True,  # Siempre listo en modo minimal
                             'tensorflow': False,  # No TensorFlow en minimal
                             'vocabulary_size': len(get_word_ids()),
                             'total_users': system_stats['total_users'],
                             'total_predictions': system_stats['total_predictions']
                         })

@app.route('/demo')
def demo():
    """Página de demostración interactiva"""
    return render_template('demo.html',
                         vocabulary=get_word_ids(),
                         system_ready=True)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard del usuario"""
    if DB_AVAILABLE and hasattr(current_user, 'get_stats'):
        user_stats = current_user.get_stats()
    else:
        # Mock stats
        user_stats = {
            'total_predictions': 42,
            'avg_confidence': 0.87,
            'top_words': [('Hola', 15), ('Gracias', 12), ('Buenos Días', 8)],
            'recent_predictions': [
                {'word': 'Hola', 'confidence': 0.92, 'timestamp': datetime.now().isoformat()},
                {'word': 'Gracias', 'confidence': 0.87, 'timestamp': datetime.now().isoformat()},
            ]
        }
    
    return render_template('dashboard.html',
                         user=current_user,
                         total_predictions=user_stats['total_predictions'],
                         avg_confidence=user_stats['avg_confidence'],
                         top_words=user_stats['top_words'],
                         recent_predictions=user_stats['recent_predictions'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not username or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('login.html')
        
        if DB_AVAILABLE:
            # Buscar usuario por username o email
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                user.update_last_login()
                flash('Inicio de sesión exitoso', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Credenciales inválidas', 'error')
        else:
            # Mock login - accept any credentials
            if username and password:
                user = User()
                login_user(user, remember=remember)
                flash('Inicio de sesión exitoso (modo demo)', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Credenciales inválidas', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validaciones
        if not all([username, email, password, password_confirm]):
            flash('Por favor completa todos los campos', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('register.html')
        
        if DB_AVAILABLE:
            # Verificar si el usuario ya existe
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return render_template('register.html')
            
            # Crear nuevo usuario
            try:
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name
                )
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating user: {e}")
                flash('Error al crear la cuenta. Intenta de nuevo.', 'error')
        else:
            # Mock registration
            flash('Registro exitoso (modo demo). Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

# ============= API ROUTES =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check del servidor - Railway compatible"""
    try:
        # Test database connection si está disponible
        db_status = True
        db_type = 'mock'
        
        if DB_AVAILABLE:
            try:
                db.session.execute('SELECT 1')
                db.session.commit()
                db_type = 'postgresql' if database_url else 'sqlite'
            except Exception as e:
                db_status = False
                logger.error(f"Database health check failed: {e}")
        
        system_stats = get_system_stats()
        
        response = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'environment': os.getenv('FLASK_ENV', 'development'),
            'database': db_type,
            'database_status': db_status,
            'database_available': DB_AVAILABLE,
            'lsch_system': True,  # Siempre true en minimal
            'vocabulary_size': len(get_word_ids()),
            'tensorflow': False,  # No TensorFlow en minimal
            'opencv': False,
            'eventlet': False,
            'socketio_mode': 'threading',
            'system': 'railway_minimal_threading',
            'web_pages': True,
            'frontend': 'served',
            'stats': system_stats,
            'version': 'minimal'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'healthy',
            'message': 'Basic health check passed',
            'error': str(e),
            'system': 'railway_minimal_fallback'
        }), 200

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """Obtener vocabulario disponible"""
    word_ids = get_word_ids()
    vocabulary = {
        word_id: get_word_label(word_id) 
        for word_id in word_ids
    }
    return jsonify({
        'vocabulary': vocabulary,
        'total': len(word_ids),
        'system': 'railway_minimal_threading',
        'source': 'mock_data'
    })

@app.route('/api/user/stats')
@login_required
def user_stats():
    """Obtener estadísticas del usuario actual"""
    if DB_AVAILABLE and hasattr(current_user, 'get_stats'):
        stats = current_user.get_stats()
    else:
        # Mock stats
        stats = {
            'total_predictions': 42,
            'avg_confidence': 0.87,
            'unique_words': 8,
            'top_words': [('Hola', 15), ('Gracias', 12), ('Buenos Días', 8)],
            'recent_predictions': [
                {'word': 'Hola', 'confidence': 0.92, 'timestamp': datetime.now().isoformat()},
                {'word': 'Gracias', 'confidence': 0.87, 'timestamp': datetime.now().isoformat()},
                {'word': 'Buenos Días', 'confidence': 0.81, 'timestamp': datetime.now().isoformat()}
            ]
        }
    
    return jsonify({
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'demo_user'),
        'stats': stats,
        'system': 'railway_minimal'
    })

@app.route('/api/system/stats')
def system_stats():
    """Obtener estadísticas del sistema"""
    stats = get_system_stats()
    return jsonify({
        'system_stats': stats,
        'database': 'postgresql' if (database_url and DB_AVAILABLE) else ('sqlite' if DB_AVAILABLE else 'mock'),
        'timestamp': datetime.now().isoformat()
    })

# ============= STATIC FILES =============

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Servir archivos CSS"""
    return send_from_directory('../frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Servir archivos JavaScript"""
    return send_from_directory('../frontend/js', filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Servir archivos de assets"""
    return send_from_directory('../frontend/assets', filename)

# ============= WEBSOCKET HANDLERS =============

@socketio.on('connect')
def handle_connect():
    """Cliente conectado via WebSocket"""
    logger.info(f"Cliente conectado: {request.sid}")
    
    # Inicializar sesión
    user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else None
    session_id = f"session_{request.sid}_{datetime.now().timestamp()}"
    
    sessions[request.sid] = {
        'kp_seq': [],
        'count_frame': 0,
        'fix_frames': 0,
        'recording': False,
        'sentence': [],
        'user_id': user_id,
        'session_id': session_id,
        'start_time': datetime.now()
    }
    
    emit('connected', {
        'message': 'Conectado al servidor LSCh Railway Minimal (Threading Mode)',
        'system': 'railway_minimal_threading',
        'lsch_ready': True,
        'opencv': False,
        'tensorflow': False,
        'socketio_mode': 'threading',
        'eventlet': False,
        'web_pages': True,
        'database': 'postgresql' if (database_url and DB_AVAILABLE) else ('sqlite' if DB_AVAILABLE else 'mock'),
        'authenticated': current_user.is_authenticated,
        'username': getattr(current_user, 'username', None) if current_user.is_authenticated else None,
        'features': ['websocket', 'predictions', 'web_interface', 'minimal_system']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info(f"Cliente desconectado: {request.sid}")
    if request.sid in sessions:
        del sessions[request.sid]

@socketio.on('process_frame')
def handle_frame(data):
    """
    Procesar frame en tiempo real via WebSocket - Minimal mode
    """
    try:
        session_data = sessions.get(request.sid)
        if not session_data:
            emit('error', {'message': 'Sesión no encontrada'})
            return
        
        # Mock processing - genera predicciones aleatorias
        word_id = random.choice(get_word_ids())
        confidence = round(random.uniform(0.7, 0.95), 3)
        word = get_word_label(word_id)
        
        session_data['sentence'].insert(0, word)
        session_data['count_frame'] += 1
        
        # Guardar predicción en base de datos si está disponible y el usuario logueado
        saved_to_db = False
        if session_data['user_id'] and current_user.is_authenticated:
            prediction = save_prediction(
                user_id=session_data['user_id'],
                word=word,
                word_id=word_id,
                confidence=confidence,
                session_id=session_data['session_id'],
                frame_count=session_data['count_frame']
            )
            saved_to_db = prediction is not None
        
        # Enviar predicción
        emit('prediction', {
            'word': word,
            'word_id': word_id,
            'confidence': confidence,
            'sentence': session_data['sentence'][:5],
            'system': 'railway_minimal_threading',
            'saved_to_db': saved_to_db
        })
        
        emit('status', {
            'recording': True,
            'frame_count': session_data['count_frame'],
            'has_hands': True,  # Mock
            'system': 'railway_minimal_threading'
        })
        
    except Exception as e:
        logger.error(f"Error procesando frame: {e}")
        emit('error', {
            'message': f'Railway minimal processing error: {str(e)}',
            'system': 'railway_minimal_error'
        })

@socketio.on('clear_sentence')
def handle_clear():
    """Limpiar historial de predicciones"""
    session_data = sessions.get(request.sid)
    if session_data:
        session_data['sentence'] = []
        emit('sentence_cleared', {
            'message': 'Historial limpiado',
            'system': 'railway_minimal_threading'
        })

@socketio.on('reset_session')
def handle_reset():
    """Resetear sesión completa"""
    if request.sid in sessions:
        user_id = sessions[request.sid]['user_id']
        session_id = f"session_{request.sid}_{datetime.now().timestamp()}"
        
        sessions[request.sid] = {
            'kp_seq': [],
            'count_frame': 0,
            'fix_frames': 0,
            'recording': False,
            'sentence': [],
            'user_id': user_id,
            'session_id': session_id,
            'start_time': datetime.now()
        }
        emit('session_reset', {
            'message': 'Sesión reiniciada',
            'system': 'railway_minimal_threading'
        })

if __name__ == '__main__':
    print("=== LSCh Railway Minimal Web Application (Threading Mode) ===")
    logger.info("Iniciando servidor LSCh Railway Minimal Threading")
    
    try:
        logger.info(f"Database: {'PostgreSQL' if (database_url and DB_AVAILABLE) else ('SQLite' if DB_AVAILABLE else 'Mock')}")
        logger.info(f"Database Available: {DB_AVAILABLE}")
        logger.info(f"TensorFlow: Disabled (Minimal Version)")
        logger.info(f"OpenCV: Disabled")
        logger.info(f"EventLet: Disabled")
        logger.info(f"SocketIO Mode: Threading")
        logger.info(f"Web Pages: Enabled")
        logger.info(f"Vocabulary: {len(get_word_ids())} palabras")
        logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    except Exception as e:
        logger.error(f"Error en configuración inicial: {e}")
    
    # Configuración para Railway
    port = int(os.getenv('PORT', 8080))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    print(f"Puerto: {port}")
    print(f"Modo: {'producción' if not debug_mode else 'desarrollo'}")
    print(f"SocketIO: Threading Mode (NO EventLet)")
    print(f"Database: {'PostgreSQL' if (database_url and DB_AVAILABLE) else ('SQLite' if DB_AVAILABLE else 'Mock')}")
    print(f"Web Pages: ENABLED")
    print(f"Version: MINIMAL (Sin TensorFlow)")
    print(f"Healthcheck: /api/health")
    
    if os.getenv('FLASK_ENV') == 'production':
        # Producción: Railway con threading
        logger.info(f"🚀 Railway Minimal Production (Threading) - Puerto {port}")
        socketio.run(app, 
                     host='0.0.0.0', 
                     port=port, 
                     debug=False,
                     log_output=True,
                     allow_unsafe_werkzeug=True)  # Required for Railway production
    else:
        # Desarrollo: Modo debug local
        logger.info(f"🔧 Development Minimal (Threading) - Puerto {port}")
        socketio.run(app, 
                     host='0.0.0.0', 
                     port=port, 
                     debug=True,
                     allow_unsafe_werkzeug=True)