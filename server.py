import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from process_video import process_video
from evaluate_model import evaluate_model
import cv2
import numpy as np
import base64
from mediapipe.solutions.holistic import Holistic

def mediapipe_detection(image, model):
    """Run MediaPipe detection on a BGR OpenCV image and return results."""
    # Convert the BGR image to RGB before processing.
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = model.process(image_rgb)
    image_rgb.flags.writeable = True
    return results

app = Flask(__name__)

def extract_keypoints(results):
    """Extract pose, face, left and right hand landmarks from MediaPipe result and return flattened numpy array."""
    # Pose: 33 landmarks with x,y,z,visibility
    pose = np.zeros(33 * 4)
    if results.pose_landmarks:
        pose = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]).flatten()
    # Face: 468 landmarks with x,y,z
    face = np.zeros(468 * 3)
    if results.face_landmarks:
        face = np.array([[lm.x, lm.y, lm.z] for lm in results.face_landmarks.landmark]).flatten()
    # Left hand: 21 landmarks with x,y,z
    lh = np.zeros(21 * 3)
    if results.left_hand_landmarks:
        lh = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark]).flatten()
    # Right hand: 21 landmarks with x,y,z
    rh = np.zeros(21 * 3)
    if results.right_hand_landmarks:
        rh = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten()
    return np.concatenate([pose, face, lh, rh])

# Try to load a trained model and word ids if available, otherwise provide a safe dummy.
model = None
word_ids = []
try:
    from tensorflow.keras.models import load_model
    import json
    model = load_model('model.h5')
    if os.path.exists('word_ids.json'):
        with open('word_ids.json', 'r', encoding='utf-8') as f:
            word_ids = json.load(f)
    else:
        word_ids = ['<UNK>']
except Exception:
    class DummyModel:
        def predict(self, x):
            # return a single-class prediction with probability 1.0 to avoid crashes when no real model is present
            return np.array([[1.0]])
    model = DummyModel()
    word_ids = ['<UNK>']

@app.route('/')
def hello():
    return 'LSP Translate'

@app.route('/upload_video', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    file_name = secure_filename(video_file.filename)
    root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_file = os.path.join(root_path, 'tmp', file_name)
    os.makedirs(os.path.dirname(tmp_file), exist_ok=True)
    video_file.save(tmp_file)
    
    video_processed = process_video(tmp_file)
    resp = evaluate_model(video_processed)
    resp = [r.upper() for r in resp][::-1]
    
    return " - ".join(resp)

@app.route('/translate_frame', methods=['POST'])
def translate_frame():
    """Recibe un frame base64 y devuelve la predicción"""
    
    # Recibe imagen en base64
    image_data = request.json.get('image')
    if not image_data:
        return jsonify({'error': 'no image provided'}), 400
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({'error': 'invalid image data'}), 400
    
    # Procesa con MediaPipe
    with Holistic() as holistic_model:
        results = mediapipe_detection(frame, holistic_model)
        keypoints = extract_keypoints(results)
    
    # Predice
    prediction = model.predict(np.expand_dims(keypoints, axis=0))
    word_id = word_ids[np.argmax(prediction)]
    confidence = float(np.max(prediction))
    
    return jsonify({
        'word': word_id,
        'confidence': confidence
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)