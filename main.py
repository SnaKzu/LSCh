import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PyQt5.uic import loadUi

import numpy as np
try:
    import tensorflow as tf
    load_model = tf.keras.models.load_model
except Exception:
    try:
        from keras.models import load_model
    except Exception:
        raise ImportError("Could not import 'load_model' from tensorflow.keras or keras. Install TensorFlow or Keras.")
import mediapipe as mp
from evaluate_model import normalize_keypoints
from helpers import *
from constants import *
from text_to_speech import text_to_speech
from logger_config import get_logger

# Configurar logger
logger = get_logger(__name__)


class VideoRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Inicializando aplicación GUI LSP")
        
        try:
            loadUi('mainwindow.ui', self)
            logger.debug("UI cargada correctamente")
        except Exception as e:
            logger.error(f"Error cargando UI: {e}", exc_info=True)
            raise
        
        self.capture = cv2.VideoCapture(0)
        
        if not self.capture.isOpened():
            logger.error("No se pudo abrir la cámara")
            raise RuntimeError("No se pudo abrir la cámara")
        
        logger.info("Cámara inicializada correctamente")
        
        self.init_lsp()
        
        # self.btn_start.clicked.connect(self.start_recording)
        # self.btn_stop.clicked.connect(self.stop_recording)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30ms
    
    def init_lsp(self):
        self.holistic_model = mp.solutions.holistic.Holistic()
        self.kp_seq, self.sentence = [], []
        self.count_frame = 0
        self.fix_frames = 0
        self.margin_frame = 1
        self.delay_frames = 3
        self.model = load_model(MODEL_PATH)
        self.recording = False
    
    def update_frame(self):
        word_ids = get_word_ids(WORDS_JSON_PATH)
        ret, frame = self.capture.read()
        if not ret: return
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = mediapipe_detection(frame, self.holistic_model)
        
        if there_hand(results) or self.recording:
            self.recording = False
            self.count_frame += 1
            if self.count_frame > self.margin_frame:
                self.kp_seq.append(extract_keypoints(results))
            
        else:
            if self.count_frame >= MIN_LENGTH_FRAMES + self.margin_frame:
                self.fix_frames += 1
                if self.fix_frames < self.delay_frames:
                    self.recording = True
                    return
                
                self.kp_seq = self.kp_seq[: - (self.margin_frame + self.delay_frames)]
                kp_normalized = normalize_keypoints(self.kp_seq, int(MODEL_FRAMES))
                res = self.model.predict(np.expand_dims(kp_normalized, axis=0))[0]
                
                if res[np.argmax(res)] > 0.7:
                    word_id = word_ids[np.argmax(res)].split('-')[0]
                    sent = words_text.get(word_id)
                    self.sentence.insert(0, sent)
                    text_to_speech(sent) # ONLY LOCAL (NO SERVER)
            
            self.recording = False
            self.fix_frames = 0
            self.count_frame = 0
            self.kp_seq = []
        
        self.lbl_output.setText(" - ".join(self.sentence))
        draw_keypoints(image, results)
        
        height, width, channel = image.shape
        step = channel * width
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        
        scaled_qImg = qImg.scaled(self.lbl_video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.lbl_video.setPixmap(QPixmap.fromImage(scaled_qImg))

    # def start_recording(self):
    #     if not self.recording:
    #         self.recording = True
    #         # self.video_writer = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
    #         self.btn_start.setEnabled(False)
    #         self.btn_stop.setEnabled(True)
    
    # def stop_recording(self):
    #     if self.recording:
    #         self.recording = False
    #         # self.video_writer.release()
    #         self.btn_start.setEnabled(True)
    #         self.btn_stop.setEnabled(False)
    
    def closeEvent(self, event):
        self.capture.release()
        # if self.is_recording:
            # self.video_writer.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoRecorder()
    window.show()
    # window.showFullScreen()
    sys.exit(app.exec_())
