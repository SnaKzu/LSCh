import cv2
import numpy as np

def augment_frame(frame):
    """Aplica transformaciones aleatorias"""
    augmented = []
    
    # Original
    augmented.append(frame)
    
    # Espejo horizontal
    augmented.append(cv2.flip(frame, 1))
    
    # Rotación ligera
    angle = np.random.uniform(-10, 10)
    M = cv2.getRotationMatrix2D((frame.shape[1]//2, frame.shape[0]//2), angle, 1)
    rotated = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
    augmented.append(rotated)
    
    # Brillo
    bright = cv2.convertScaleAbs(frame, alpha=1.2, beta=20)
    augmented.append(bright)
    
    return augmented

# Úsar en create_keypoints.py para multiplicar los datos