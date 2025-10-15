"""
Backend Flask para LSP Web Application
Reconocimiento de Lengua de Señas Peruana en tiempo real
Con autenticación de usuarios
"""

import os
import sys
import cv2
import base64
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import mediapipe as mp

# Añadir directorio raíz al path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tensorflow.keras.models import load_model
from helpers import mediapipe_detection, extract_keypoints, there_hand
from evaluate_model import normalize_keypoints
from config_manager import ConfigManager
from logger_config import get_logger

# Importar modelos de base de datos
from models import db, User, Prediction

# Configuración
logger = get_logger(__name__)
config = ConfigManager()

app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='',
            template_folder='../frontend')
app.config['SECRET_KEY'] = 'lsp-secret-key-2025-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../lsp_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db.init_app(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inicializar MediaPipe y Modelo
holistic_model = mp.solutions.holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

try:
    model = load_model(config.get_model_path())
    logger.info(f"Modelo cargado: {config.get_model_path()}")
except Exception as e:
    logger.error(f"Error cargando modelo: {e}")
    model = None

# Variables globales para sesión
sessions = {}


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/demo')
@login_required
def demo():
    """Página de demo interactivo - requiere login"""
    return send_from_directory('../frontend', 'demo.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        if not username or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('login.html')
        
        # Buscar usuario por username o email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tu cuenta ha sido desactivada', 'error')
                return render_template('login.html')
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            logger.info(f"Usuario {user.username} ha iniciado sesión")
            flash(f'¡Bienvenido de vuelta, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            logger.warning(f"Intento de login fallido para: {username}")
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validaciones
        if not all([username, email, password, full_name]):
            flash('Por favor completa todos los campos', 'error')
            return render_template('register.html')
        
        if len(username) < 3 or len(username) > 20:
            flash('El usuario debe tener entre 3 y 20 caracteres', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('register.html')
        
        # Crear nuevo usuario
        try:
            new_user = User(
                username=username,
                email=email,
                full_name=full_name
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"Nuevo usuario registrado: {username}")
            flash('¡Cuenta creada exitosamente! Por favor inicia sesión', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al registrar usuario: {e}")
            flash('Error al crear la cuenta. Por favor intenta de nuevo', 'error')
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    username = current_user.username
    logout_user()
    logger.info(f"Usuario {username} ha cerrado sesión")
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard del usuario"""
    # Obtener estadísticas del usuario
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    
    # Últimas predicciones
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.timestamp.desc())\
        .limit(10)\
        .all()
    
    # Calcular promedio de confianza
    all_predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    avg_confidence = sum(p.confidence for p in all_predictions) / len(all_predictions) if all_predictions else 0
    
    # Palabras más usadas
    word_counts = {}
    for pred in all_predictions:
        word_counts[pred.word] = word_counts.get(pred.word, 0) + 1
    
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template('dashboard.html',
                         user=current_user,
                         total_predictions=total_predictions,
                         recent_predictions=recent_predictions,
                         avg_confidence=avg_confidence,
                         top_words=top_words)


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Servir archivos CSS"""
    return send_from_directory('../frontend/css', filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Servir archivos JavaScript"""
    return send_from_directory('../frontend/js', filename)


@app.route('/favicon.ico')
def favicon():
    """Servir favicon"""
    return send_from_directory('../frontend', 'favicon.ico')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check del servidor"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'vocabulary_size': len(config.get_word_ids()),
        'words': config.get_word_ids()
    })


@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """Obtener vocabulario disponible"""
    word_ids = config.get_word_ids()
    vocabulary = {
        word_id: config.get_word_label(word_id) 
        for word_id in word_ids
    }
    return jsonify({
        'vocabulary': vocabulary,
        'total': len(word_ids)
    })


@app.route('/api/predict-frame', methods=['POST'])
def predict_frame():
    """
    Predecir seña desde un frame individual (base64)
    """
    try:
        data = request.get_json()
        
        if 'frame' not in data:
            return jsonify({'error': 'No frame provided'}), 400
        
        # Decodificar imagen base64
        img_data = base64.b64decode(data['frame'].split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Procesar con MediaPipe
        results = mediapipe_detection(frame, holistic_model)
        
        # Verificar si hay manos
        has_hands = there_hand(results)
        
        response = {
            'has_hands': bool(has_hands),
            'keypoints_detected': {
                'pose': results.pose_landmarks is not None,
                'face': results.face_landmarks is not None,
                'left_hand': results.left_hand_landmarks is not None,
                'right_hand': results.right_hand_landmarks is not None
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error en predict_frame: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Cliente conectado via WebSocket"""
    logger.info(f"Cliente conectado: {request.sid}")
    
    # Inicializar sesión
    sessions[request.sid] = {
        'kp_seq': [],
        'count_frame': 0,
        'fix_frames': 0,
        'recording': False,
        'sentence': [],
        'user_id': current_user.id if current_user.is_authenticated else None
    }
    
    emit('connected', {'message': 'Conectado al servidor LSP'})


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info(f"Cliente desconectado: {request.sid}")
    if request.sid in sessions:
        del sessions[request.sid]


@socketio.on('process_frame')
def handle_frame(data):
    """
    Procesar frame en tiempo real via WebSocket
    """
    try:
        session = sessions.get(request.sid)
        if not session:
            emit('error', {'message': 'Sesión no encontrada'})
            return
        
        # Decodificar frame
        img_data = base64.b64decode(data['frame'].split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Procesar con MediaPipe
        results = mediapipe_detection(frame, holistic_model)
        
        # Parámetros de configuración
        margin_frame = config.capture.margin_frame
        delay_frames = config.capture.delay_frames
        min_length_frames = config.model.min_length_frames
        
        # Lógica de reconocimiento (igual que main.py)
        if there_hand(results) or session['recording']:
            session['recording'] = False
            session['count_frame'] += 1
            
            if session['count_frame'] > margin_frame:
                keypoints = extract_keypoints(results)
                session['kp_seq'].append(keypoints)
            
            # Enviar estado
            emit('status', {
                'recording': True,
                'frame_count': session['count_frame'],
                'has_hands': True
            })
            
        else:
            # No hay manos detectadas
            if session['count_frame'] >= min_length_frames + margin_frame:
                session['fix_frames'] += 1
                
                if session['fix_frames'] < delay_frames:
                    session['recording'] = True
                    return
                
                # Procesar secuencia
                kp_seq = session['kp_seq'][: - (margin_frame + delay_frames)]
                
                if len(kp_seq) >= min_length_frames:
                    kp_normalized = normalize_keypoints(kp_seq, config.model.frames)
                    prediction = model.predict(np.expand_dims(kp_normalized, axis=0))[0]
                    
                    confidence = float(np.max(prediction))
                    
                    if confidence > config.evaluation.confidence_threshold:
                        word_idx = int(np.argmax(prediction))
                        word_ids = config.get_word_ids()
                        word_id = word_ids[word_idx].split('-')[0]
                        word_label = config.get_word_label(word_id)
                        
                        session['sentence'].insert(0, word_label)
                        
                        # Guardar predicción en base de datos si el usuario está autenticado
                        if session.get('user_id'):
                            try:
                                new_prediction = Prediction(
                                    user_id=session['user_id'],
                                    word=word_label,
                                    word_id=word_id,
                                    confidence=confidence,
                                    session_id=request.sid
                                )
                                db.session.add(new_prediction)
                                db.session.commit()
                            except Exception as e:
                                logger.error(f"Error guardando predicción: {e}")
                                db.session.rollback()
                        
                        # Enviar predicción
                        emit('prediction', {
                            'word': word_label,
                            'word_id': word_id,
                            'confidence': confidence,
                            'sentence': session['sentence'][:5]  # Últimas 5 palabras
                        })
                        
                        logger.info(f"Predicción: {word_label} ({confidence:.2%})")
            
            # Resetear estado
            session['recording'] = False
            session['fix_frames'] = 0
            session['count_frame'] = 0
            session['kp_seq'] = []
            
            emit('status', {
                'recording': False,
                'frame_count': 0,
                'has_hands': False
            })
            
    except Exception as e:
        logger.error(f"Error procesando frame: {e}", exc_info=True)
        emit('error', {'message': str(e)})


@socketio.on('clear_sentence')
def handle_clear():
    """Limpiar historial de predicciones"""
    session = sessions.get(request.sid)
    if session:
        session['sentence'] = []
        emit('sentence_cleared', {'message': 'Historial limpiado'})


@socketio.on('reset_session')
def handle_reset():
    """Resetear sesión completa"""
    if request.sid in sessions:
        sessions[request.sid] = {
            'kp_seq': [],
            'count_frame': 0,
            'fix_frames': 0,
            'recording': False,
            'sentence': []
        }
        emit('session_reset', {'message': 'Sesión reiniciada'})


if __name__ == '__main__':
    logger.info("Iniciando servidor LSP Web Application")
    logger.info(f"Frontend: {app.static_folder}")
    logger.info(f"Vocabulario: {len(config.get_word_ids())} palabras")
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
        logger.info("Base de datos inicializada")
    
    # Modo desarrollo con hot reload
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=5000, 
                 debug=True,
                 allow_unsafe_werkzeug=True)
