import os
import pandas as pd
from mediapipe.python.solutions.holistic import Holistic
from helpers import *
from constants import *
from logger_config import get_logger

# Configurar logger
logger = get_logger(__name__)

def create_keypoints(word_id, words_path, hdf_path):
    '''
    ### CREAR KEYPOINTS PARA UNA PALABRA
    Recorre la carpeta de frames de la palabra y guarda sus keypoints en `hdf_path`
    '''
    logger.info(f"Procesando palabra: {word_id}")
    data = pd.DataFrame([])
    frames_path = os.path.join(words_path, word_id)
    
    with Holistic() as holistic:
        sample_list = os.listdir(frames_path)
        sample_count = len(sample_list)
        logger.info(f"  Encontradas {sample_count} muestras")
        
        for n_sample, sample_name in enumerate(sample_list, start=1):
            sample_path = os.path.join(frames_path, sample_name)
            keypoints_sequence = get_keypoints(holistic, sample_path)
            data = insert_keypoints_sequence(data, n_sample, keypoints_sequence)
            
            if n_sample % 10 == 0 or n_sample == sample_count:
                logger.debug(f"  Progreso: {n_sample}/{sample_count}")

    data.to_hdf(hdf_path, key="data", mode="w")
    logger.info(f"  ✓ Keypoints guardados: {hdf_path} ({sample_count} muestras)")


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("INICIANDO CREACIÓN DE KEYPOINTS")
    logger.info("=" * 70)
    # Crea la carpeta `keypoints` en caso no exista
    create_folder(KEYPOINTS_PATH)
    logger.info(f"Directorio de keypoints: {KEYPOINTS_PATH}")
    
    # GENERAR TODAS LAS PALABRAS
    word_ids = [word for word in os.listdir(os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH))]
    
    # GENERAR PARA UNA PALABRA O CONJUNTO
    # word_ids = ["bien"]
    # word_ids = ["buenos_dias", "como_estas", "disculpa", "gracias", "hola-der", "hola-izq", "mal", "mas_o_menos", "me_ayudas", "por_favor"]
    
    logger.info(f"Procesando {len(word_ids)} palabras")
    
    for idx, word_id in enumerate(word_ids, 1):
        hdf_path = os.path.join(KEYPOINTS_PATH, f"{word_id}.h5")
        logger.info(f"[{idx}/{len(word_ids)}] {word_id}")
        try:
            create_keypoints(word_id, FRAME_ACTIONS_PATH, hdf_path)
        except Exception as e:
            logger.error(f"  ❌ Error procesando '{word_id}': {e}", exc_info=True)
    
    logger.info("=" * 70)
    logger.info("✓ CREACIÓN DE KEYPOINTS COMPLETADA")
    logger.info("=" * 70)