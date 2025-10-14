import os
from flask import Flask, request
from werkzeug.utils import secure_filename
from process_video import process_video
from evaluate_model import evaluate_model

app = Flask(__name__)

@app.route('/')
def hello():
    return 'LSP Translate'

@app.route('/upload_video', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    file_name = secure_filename(video_file.filename)
    root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_file = os.path.join(root_path, 'tmp', file_name)
    video_file.save(tmp_file)
    
    video_processed = process_video(tmp_file)
    resp = evaluate_model(video_processed)
    resp = [r.upper() for r in resp][::-1]
    
    return " - ".join(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/translate_frame', methods=['POST'])
def translate_frame():
    """Recibe un frame base64 y devuelve la predicción"""
    
    # Recibe imagen en base64
    image_data = request.json['image']
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
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