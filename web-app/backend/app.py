"""
Backend Flask para LSP Web Application
Reconocimiento de Lengua de Señas Peruana en tiempo real
"""

import os
import sys
import cv2
import base64
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mediapipe as mp

# Añadir directorio raíz al path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tensorflow.keras.models import load_model
from helpers import mediapipe_detection, extract_keypoints, there_hand
from evaluate_model import normalize_keypoints
from config_manager import ConfigManager
from logger_config import get_logger

# Configuración
logger = get_logger(__name__)
config = ConfigManager()

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
app.config['SECRET_KEY'] = 'lsp-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    return send_from_directory('../frontend', 'index.html')


@app.route('/demo')
def demo():
    """Página de demo interactivo"""
    return send_from_directory('../frontend', 'demo.html')


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
        'sentence': []
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
    
    # Modo desarrollo con hot reload
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=5000, 
                 debug=True,
                 allow_unsafe_werkzeug=True)
