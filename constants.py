"""
constants.py - Backward Compatibility Layer
============================================

DEPRECADO: Este archivo se mantiene solo por compatibilidad con código legacy.
Se recomienda migrar a usar config_manager.py directamente:

    # Antiguo
    from constants import MODEL_PATH, MODEL_FRAMES
    
    # Nuevo (recomendado)
    from config_manager import config
    model_path = config.get_model_path()
    model_frames = config.model.frames

Todas las importaciones de este módulo se redirigen al nuevo ConfigManager.
"""

import warnings
import cv2

# Importa todo desde el nuevo sistema de configuración
from config_manager import (
    config,
    ROOT_PATH,
    FRAME_ACTIONS_PATH,
    DATA_PATH,
    DATA_JSON_PATH,
    MODEL_FOLDER_PATH,
    MODEL_PATH,
    KEYPOINTS_PATH,
    WORDS_JSON_PATH,
    MIN_LENGTH_FRAMES,
    LENGTH_KEYPOINTS,
    MODEL_FRAMES
)

# Emite warning para fomentar migración
warnings.warn(
    "constants.py está deprecado. Use 'from config_manager import config' en su lugar.",
    DeprecationWarning,
    stacklevel=2
)

# SHOW IMAGE PARAMETERS - Usando configuración de config.yaml
FONT = getattr(cv2, config.display.font)
FONT_SIZE = config.display.font_size
FONT_POS = tuple(config.display.font_position)

# Diccionario de palabras - Ahora viene de config.yaml
words_text = config.get_word_labels_dict()


# ==================== COMPATIBILIDAD LEGACY ====================
# Estas funciones/variables se mantienen para no romper código existente

def get_word_label(word_id: str) -> str:
    """
    DEPRECADO: Use config.get_word_label(word_id)
    
    Retorna el texto legible de una palabra
    """
    warnings.warn(
        "get_word_label() está deprecado. Use config.get_word_label() en su lugar.",
        DeprecationWarning,
        stacklevel=2
    )
    return config.get_word_label(word_id)


if __name__ == "__main__":
    print("⚠️  Este módulo está deprecado. Use config_manager.py")
    print("\nVariables disponibles por compatibilidad:")
    print(f"  ROOT_PATH: {ROOT_PATH}")
    print(f"  MODEL_PATH: {MODEL_PATH}")
    print(f"  MODEL_FRAMES: {MODEL_FRAMES}")
    print(f"  LENGTH_KEYPOINTS: {LENGTH_KEYPOINTS}")
    print(f"\nTotal de palabras: {len(words_text)}")
