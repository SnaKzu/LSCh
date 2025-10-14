"""
ConfigManager - Gestor de configuración centralizado
=====================================================

Este módulo provee acceso tipo-seguro a toda la configuración del proyecto
desde el archivo config.yaml centralizado.

Uso:
    from config_manager import config
    
    # Acceso simple
    model_frames = config.model.frames
    confidence = config.evaluation.confidence_threshold
    
    # Paths absolutos
    model_path = config.get_model_path()
    keypoints_path = config.get_keypoints_path()
"""

import os
import yaml
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigDict:
    """Clase helper para acceder a diccionarios como atributos"""
    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigDict(value))
            else:
                setattr(self, key, value)
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def get(self, key, default=None):
        """Método get similar a dict.get()"""
        return getattr(self, key, default)
    
    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items()}
        return f"ConfigDict({attrs})"


class ConfigManager:
    """
    Gestor de configuración que carga y provee acceso a config.yaml
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el gestor de configuración
        
        Args:
            config_path: Ruta al archivo config.yaml. Si es None, busca en el directorio del proyecto.
        """
        if config_path is None:
            # Busca config.yaml en el directorio del script
            self.root_path = Path(__file__).parent.absolute()
            config_path = self.root_path / "config.yaml"
        else:
            config_path = Path(config_path)
            self.root_path = config_path.parent.absolute()
        
        self.config_path = config_path
        self._load_config()
        self._setup_paths()
    
    def _load_config(self):
        """Carga el archivo YAML de configuración"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Configuración cargada desde: {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error al parsear config.yaml: {e}")
            raise
        
        # Crea objetos ConfigDict para acceso por atributos
        for key, value in self._config.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigDict(value))
            else:
                setattr(self, key, value)
    
    def _setup_paths(self):
        """Configura rutas absolutas basadas en el root del proyecto"""
        # Paths base
        self.FRAME_ACTIONS_PATH = self.root_path / self.paths.frame_actions
        self.DATA_PATH = self.root_path / self.paths.data
        self.MODEL_FOLDER_PATH = self.root_path / self.paths.models
        self.KEYPOINTS_PATH = self.root_path / self.paths.keypoints
        
        # Archivos específicos
        self.DATA_JSON_PATH = self.root_path / self.paths.data_json
        self.WORDS_JSON_PATH = self.root_path / self.paths.words_json
        self.MODEL_PATH = self.MODEL_FOLDER_PATH / self.model.model_filename
    
    # ==================== MÉTODOS DE ACCESO A PATHS ====================
    
    def get_model_path(self) -> Path:
        """Retorna la ruta absoluta del modelo entrenado"""
        return self.MODEL_PATH
    
    def get_keypoints_path(self, word_id: str = None) -> Path:
        """
        Retorna la ruta a la carpeta de keypoints o a un archivo específico
        
        Args:
            word_id: Si se especifica, retorna la ruta al archivo .h5 de esa palabra
        """
        if word_id:
            return self.KEYPOINTS_PATH / f"{word_id}.h5"
        return self.KEYPOINTS_PATH
    
    def get_frame_actions_path(self, word_id: str = None) -> Path:
        """
        Retorna la ruta a la carpeta frame_actions o a una palabra específica
        
        Args:
            word_id: Si se especifica, retorna la ruta a la carpeta de esa palabra
        """
        if word_id:
            return self.FRAME_ACTIONS_PATH / word_id
        return self.FRAME_ACTIONS_PATH
    
    # ==================== MÉTODOS DE ACCESO A CONFIGURACIÓN ====================
    
    def get_word_ids(self) -> List[str]:
        """Retorna la lista de IDs de palabras en el vocabulario"""
        return self.vocabulary.word_ids.copy()
    
    def get_word_label(self, word_id: str) -> str:
        """
        Retorna el texto legible de una palabra
        
        Args:
            word_id: ID de la palabra (ej: "buenos_dias")
            
        Returns:
            Texto formateado (ej: "BUENOS DÍAS")
        """
        # Extrae el ID base (sin sufijos como -der, -izq)
        base_id = word_id.split('-')[0]
        return self.vocabulary.word_labels.get(base_id, word_id.upper())
    
    def get_word_labels_dict(self) -> Dict[str, str]:
        """Retorna diccionario completo de word_id -> label"""
        return {k: v for k, v in self.vocabulary.word_labels.__dict__.items()}
    
    def get_model_config(self) -> Dict[str, Any]:
        """Retorna configuración completa del modelo"""
        return {
            'frames': self.model.frames,
            'keypoints_length': self.model.keypoints_length,
            'min_length_frames': self.model.min_length_frames,
        }
    
    def get_network_config(self) -> Dict[str, Any]:
        """Retorna configuración de la arquitectura de red"""
        return {k: v for k, v in self.network.__dict__.items()}
    
    def get_training_config(self) -> Dict[str, Any]:
        """Retorna configuración de entrenamiento"""
        return {k: v for k, v in self.training.__dict__.items()}
    
    # ==================== UTILIDADES ====================
    
    def create_directories(self):
        """Crea todas las carpetas necesarias si no existen"""
        directories = [
            self.FRAME_ACTIONS_PATH,
            self.DATA_PATH,
            self.MODEL_FOLDER_PATH,
            self.KEYPOINTS_PATH,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio verificado/creado: {directory}")
    
    def validate_config(self) -> bool:
        """
        Valida que la configuración sea coherente
        
        Returns:
            True si la configuración es válida
        
        Raises:
            ValueError: Si hay errores en la configuración
        """
        errors = []
        
        # Validar que hay palabras en el vocabulario
        if not self.vocabulary.word_ids:
            errors.append("El vocabulario está vacío")
        
        # Validar que todas las palabras tienen label
        for word_id in self.vocabulary.word_ids:
            base_id = word_id.split('-')[0]
            if not hasattr(self.vocabulary.word_labels, base_id):
                errors.append(f"Palabra '{word_id}' no tiene label definido")
        
        # Validar valores numéricos
        if self.model.frames <= 0:
            errors.append("model.frames debe ser > 0")
        
        if not 0.0 <= self.evaluation.confidence_threshold <= 1.0:
            errors.append("evaluation.confidence_threshold debe estar entre 0 y 1")
        
        if self.training.validation_split <= 0 or self.training.validation_split >= 1:
            errors.append("training.validation_split debe estar entre 0 y 1")
        
        if errors:
            raise ValueError("Errores en la configuración:\n" + "\n".join(f"  - {e}" for e in errors))
        
        logger.info("✓ Configuración validada correctamente")
        return True
    
    def reload(self):
        """Recarga la configuración desde el archivo"""
        logger.info("Recargando configuración...")
        self._load_config()
        self._setup_paths()
    
    def __repr__(self):
        return f"ConfigManager(config_path='{self.config_path}')"


# ==================== INSTANCIA GLOBAL ====================
# Singleton para acceso fácil desde cualquier módulo

try:
    config = ConfigManager()
    config.validate_config()
except Exception as e:
    logger.error(f"Error al inicializar ConfigManager: {e}")
    raise


# ==================== BACKWARD COMPATIBILITY ====================
# Para mantener compatibilidad con código existente que importa de constants.py

# Exporta constantes principales
ROOT_PATH = config.root_path
FRAME_ACTIONS_PATH = config.FRAME_ACTIONS_PATH
DATA_PATH = config.DATA_PATH
MODEL_FOLDER_PATH = config.MODEL_FOLDER_PATH
KEYPOINTS_PATH = config.KEYPOINTS_PATH
DATA_JSON_PATH = config.DATA_JSON_PATH
WORDS_JSON_PATH = config.WORDS_JSON_PATH
MODEL_PATH = config.MODEL_PATH

MIN_LENGTH_FRAMES = config.model.min_length_frames
LENGTH_KEYPOINTS = config.model.keypoints_length
MODEL_FRAMES = config.model.frames


if __name__ == "__main__":
    # Setup logging para testing
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("=" * 60)
    print("CONFIGURACIÓN DEL PROYECTO LSP")
    print("=" * 60)
    
    print(f"\n📁 Rutas:")
    print(f"  Root: {config.root_path}")
    print(f"  Modelo: {config.get_model_path()}")
    print(f"  Keypoints: {config.get_keypoints_path()}")
    
    print(f"\n🧠 Modelo:")
    print(f"  Frames: {config.model.frames}")
    print(f"  Keypoints: {config.model.keypoints_length}")
    print(f"  Min frames: {config.model.min_length_frames}")
    
    print(f"\n📚 Vocabulario ({len(config.get_word_ids())} palabras):")
    for word_id in config.get_word_ids()[:5]:
        print(f"  - {word_id}: {config.get_word_label(word_id)}")
    print(f"  ... y {len(config.get_word_ids()) - 5} más")
    
    print(f"\n🎓 Entrenamiento:")
    print(f"  Epochs: {config.training.epochs}")
    print(f"  Batch size: {config.training.batch_size}")
    print(f"  Validation: {config.training.validation_split * 100}%")
    
    print(f"\n🔬 Evaluación:")
    print(f"  Confianza mínima: {config.evaluation.confidence_threshold * 100}%")
    
    print(f"\n✓ Configuración validada correctamente")
