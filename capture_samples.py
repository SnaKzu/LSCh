import os
import cv2
import numpy as np
from mediapipe.python.solutions.holistic import Holistic
from helpers import create_folder, draw_keypoints, mediapipe_detection, save_frames, there_hand
from constants import FONT, FONT_POS, FONT_SIZE, FRAME_ACTIONS_PATH, ROOT_PATH
from datetime import datetime
from logger_config import get_logger

# Configurar logger
logger = get_logger(__name__)


def capture_samples(path, margin_frame=1, min_cant_frames=5, delay_frames=3):
    '''
    ### CAPTURA DE MUESTRAS PARA UNA PALABRA
    Recibe como parámetro la ubicación de guardado y guarda los frames
    
    `path` ruta de la carpeta de la palabra \n
    `margin_frame` cantidad de frames que se ignoran al comienzo y al final \n
    `min_cant_frames` cantidad de frames minimos para cada muestra \n
    `delay_frames` cantidad de frames que espera antes de detener la captura después de no detectar manos
    '''
    logger.info("=" * 70)
    logger.info(f"Iniciando captura de muestras para: {os.path.basename(path)}")
    logger.info(f"Parámetros: margin={margin_frame}, min_frames={min_cant_frames}, delay={delay_frames}")
    logger.info("=" * 70)
    
    create_folder(path)
    logger.debug(f"Carpeta creada/verificada: {path}")
    
    count_frame = 0
    frames = []
    fix_frames = 0
    recording = False
    samples_captured = 0
    
    with Holistic() as holistic_model:
        logger.info("MediaPipe Holistic inicializado")
        video = cv2.VideoCapture(0)
        
        if not video.isOpened():
            logger.error("❌ No se pudo abrir la cámara")
            raise RuntimeError("No se pudo abrir la cámara")
        
        logger.info("✓ Cámara abierta correctamente")
        logger.info("Presiona 'q' para salir")
        logger.info("Listo para capturar - Haz la seña frente a la cámara...")
        
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            
            image = frame.copy()
            results = mediapipe_detection(frame, holistic_model)
            
            if there_hand(results) or recording:
                recording = False
                count_frame += 1
                if count_frame > margin_frame:
                    cv2.putText(image, 'Capturando...', FONT_POS, FONT, FONT_SIZE, (255, 50, 0))
                    frames.append(np.asarray(frame))
            else:
                if len(frames) >= min_cant_frames + margin_frame:
                    fix_frames += 1
                    if fix_frames < delay_frames:
                        recording = True
                        continue
                    frames = frames[: - (margin_frame + delay_frames)]
                    today = datetime.now().strftime('%y%m%d%H%M%S%f')
                    output_folder = os.path.join(path, f"sample_{today}")
                    create_folder(output_folder)
                    save_frames(frames, output_folder)
                    samples_captured += 1
                    logger.info(f"✓ Muestra #{samples_captured} guardada: {len(frames)} frames → {output_folder}")
                
                recording, fix_frames = False, 0
                frames, count_frame = [], 0
                cv2.putText(image, 'Listo para capturar...', FONT_POS, FONT, FONT_SIZE, (0,220, 100))
            
            draw_keypoints(image, results)
            cv2.imshow(f'Toma de muestras para "{os.path.basename(path)}"', image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                logger.info("Usuario presionó 'q' - Finalizando captura")
                break

        video.release()
        cv2.destroyAllWindows()
        
        logger.info("=" * 70)
        logger.info(f"✓ Captura finalizada: {samples_captured} muestras guardadas")
        logger.info("=" * 70)

if __name__ == "__main__":
    word_name = "buenos_dias"
    word_path = os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH, word_name)
    
    logger.info("Iniciando script de captura de muestras")
    try:
        capture_samples(word_path)
    except Exception as e:
        logger.error(f"❌ Error durante la captura: {e}", exc_info=True)
        raise
