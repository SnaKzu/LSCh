"""
Configuración global de pytest
"""
import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile

# Agregar proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_mediapipe_results():
    """Mock de resultados de MediaPipe"""
    class MockLandmark:
        def __init__(self):
            self.x = 0.5
            self.y = 0.5
            self.z = 0.5
            self.visibility = 1.0
    
    class MockLandmarks:
        def __init__(self, count):
            self.landmark = [MockLandmark() for _ in range(count)]
    
    class MockResults:
        def __init__(self):
            self.pose_landmarks = MockLandmarks(33)
            self.face_landmarks = MockLandmarks(468)
            self.left_hand_landmarks = MockLandmarks(21)
            self.right_hand_landmarks = MockLandmarks(21)
    
    return MockResults()


@pytest.fixture
def sample_keypoints():
    """Genera keypoints de ejemplo"""
    # 1662 keypoints: pose(132) + face(1404) + left_hand(63) + right_hand(63)
    return np.random.rand(1662).astype(np.float32)


@pytest.fixture
def sample_keypoints_sequence():
    """Genera secuencia de keypoints de ejemplo"""
    # Secuencia de 15 frames
    return np.random.rand(15, 1662).astype(np.float32)


@pytest.fixture
def temp_config_file():
    """Crea un archivo de configuración temporal"""
    config_content = """
model:
  frames: 15
  keypoints_length: 1662
  min_length_frames: 5
  model_filename: "actions_15.keras"

capture:
  margin_frame: 1
  delay_frames: 3
  jpeg_quality: 50

training:
  epochs: 500
  batch_size: 8
  validation_split: 0.05
  early_stopping_patience: 10
  random_seed: 42

evaluation:
  confidence_threshold: 0.8

network:
  lstm1_units: 64
  lstm1_l2: 0.01
  lstm1_dropout: 0.5
  lstm2_units: 128
  lstm2_l2: 0.001
  lstm2_dropout: 0.5
  dense1_units: 64
  dense1_l2: 0.001
  dense2_units: 64
  dense2_l2: 0.001
  optimizer: "adam"
  loss: "categorical_crossentropy"
  metrics: ["accuracy"]

display:
  font: "FONT_HERSHEY_PLAIN"
  font_size: 1.5
  font_position: [5, 30]

paths:
  frame_actions: "frame_actions"
  data: "data"
  models: "models"
  keypoints: "data/keypoints"
  data_json: "data/data.json"
  words_json: "models/words.json"

vocabulary:
  word_ids:
    - "adios"
    - "bien"
    - "hola"
  
  word_labels:
    adios: "ADIÓS"
    bien: "BIEN"
    hola: "HOLA"

tts:
  language: "es"
  audio_filename: "speech.mp3"

server:
  host: "0.0.0.0"
  port: 5000
  debug: true
  upload_folder: "tmp"

mediapipe:
  min_detection_confidence: 0.5
  min_tracking_confidence: 0.5
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write(config_content)
        temp_path = f.name
    
    yield temp_path
    
    # Limpieza
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def sample_image():
    """Genera una imagen de prueba"""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_frames(tmp_path):
    """Genera frames de prueba en disco"""
    frames_dir = tmp_path / "sample_frames"
    frames_dir.mkdir()
    
    # Crear 15 frames de prueba
    for i in range(15):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        import cv2
        cv2.imwrite(str(frames_dir / f"{i+1}.jpg"), frame)
    
    return frames_dir
