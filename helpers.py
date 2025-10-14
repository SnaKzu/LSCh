"""
helpers.py - Funciones de utilidad del proyecto LSP
====================================================

Funciones reutilizables para procesamiento de video, MediaPipe,
manejo de keypoints y datos.
"""

import json
import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import logging
from typing import NamedTuple, List, Tuple
from pathlib import Path

from config_manager import config

logger = logging.getLogger(__name__)

KEYPOINTS_PATH = config.KEYPOINTS_PATH


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    return results


def create_folder(path: str):
    path_obj = Path(path)
    if not path_obj.exists():
        path_obj.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Carpeta creada: {path}")


def there_hand(results: NamedTuple) -> bool:
    return results.left_hand_landmarks or results.right_hand_landmarks


def get_word_ids(path: str = None) -> List[str]:
    if path is None:
        return config.get_word_ids()
    
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data.get('word_ids', [])
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {path}")
        return []


def draw_keypoints(image, results):
    mp.solutions.drawing_utils.draw_landmarks(
        image, results.face_landmarks, mp.solutions.holistic.FACEMESH_CONTOURS,
        mp.solutions.drawing_utils.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
        mp.solutions.drawing_utils.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1),
    )
    
    mp.solutions.drawing_utils.draw_landmarks(
        image, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS,
        mp.solutions.drawing_utils.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
        mp.solutions.drawing_utils.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2),
    )
    
    mp.solutions.drawing_utils.draw_landmarks(
        image, results.left_hand_landmarks, mp.solutions.holistic.HAND_CONNECTIONS,
        mp.solutions.drawing_utils.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
        mp.solutions.drawing_utils.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2),
    )
    
    mp.solutions.drawing_utils.draw_landmarks(
        image, results.right_hand_landmarks, mp.solutions.holistic.HAND_CONNECTIONS,
        mp.solutions.drawing_utils.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
        mp.solutions.drawing_utils.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2),
    )


def save_frames(frames: List[np.ndarray], output_folder: str):
    create_folder(output_folder)
    jpeg_quality = config.capture.jpeg_quality
    
    for num_frame, frame in enumerate(frames):
        frame_path = os.path.join(output_folder, f"{num_frame + 1}.jpg")
        cv2.imwrite(
            frame_path,
            cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA),
            [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        )


def extract_keypoints(results) -> np.ndarray:
    pose = np.array([
        [res.x, res.y, res.z, res.visibility]
        for res in results.pose_landmarks.landmark
    ]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    
    face = np.array([
        [res.x, res.y, res.z]
        for res in results.face_landmarks.landmark
    ]).flatten() if results.face_landmarks else np.zeros(468 * 3)
    
    lh = np.array([
        [res.x, res.y, res.z]
        for res in results.left_hand_landmarks.landmark
    ]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    
    rh = np.array([
        [res.x, res.y, res.z]
        for res in results.right_hand_landmarks.landmark
    ]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)
    
    keypoints = np.concatenate([pose, face, lh, rh])
    
    assert keypoints.shape == (config.model.keypoints_length,), f"Keypoints shape incorrecto: {keypoints.shape}"
    
    return keypoints


def get_keypoints(model, sample_path: str) -> np.ndarray:
    kp_seq = []
    frame_files = sorted(os.listdir(sample_path))
    
    for img_name in frame_files:
        if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        
        img_path = os.path.join(sample_path, img_name)
        frame = cv2.imread(img_path)
        
        if frame is None:
            logger.warning(f"No se pudo leer frame: {img_path}")
            continue
        
        results = mediapipe_detection(frame, model)
        kp_frame = extract_keypoints(results)
        kp_seq.append(kp_frame)
    
    return np.array(kp_seq)


def insert_keypoints_sequence(df: pd.DataFrame, n_sample: int, kp_seq: np.ndarray) -> pd.DataFrame:
    for frame, keypoints in enumerate(kp_seq):
        data = {'sample': n_sample, 'frame': frame + 1, 'keypoints': [keypoints]}
        df_keypoints = pd.DataFrame(data)
        df = pd.concat([df, df_keypoints], ignore_index=True)
    
    return df


def get_sequences_and_labels(words_id: List[str]) -> Tuple[List, List]:
    sequences, labels = [], []
    
    for word_index, word_id in enumerate(words_id):
        hdf_path = config.get_keypoints_path(word_id)
        
        if not hdf_path.exists():
            logger.warning(f"Archivo de keypoints no encontrado: {hdf_path}")
            continue
        
        try:
            data = pd.read_hdf(hdf_path, key='data')
            
            for sample_num, df_sample in data.groupby('sample'):
                seq_keypoints = [row['keypoints'] for _, row in df_sample.iterrows()]
                sequences.append(seq_keypoints)
                labels.append(word_index)
            
            logger.debug(f"Cargadas muestras de '{word_id}': {len(data.groupby('sample'))}")
        
        except Exception as e:
            logger.error(f"Error al leer {hdf_path}: {e}")
            continue
    
    logger.info(f"Total de secuencias cargadas: {len(sequences)}")
    return sequences, labels


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing helpers.py...")
    print(f"Configuración cargada: {len(config.get_word_ids())} palabras")
    print(f"Keypoints path: {config.KEYPOINTS_PATH}")
    print(" Módulo cargado correctamente")
