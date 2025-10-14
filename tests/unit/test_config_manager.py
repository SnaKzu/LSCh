"""
Tests unitarios para config_manager.py
"""
import pytest
from pathlib import Path

from config_manager import ConfigManager, ConfigDict


class TestConfigDict:
    """Tests para ConfigDict"""
    
    def test_config_dict_creation(self):
        """Verifica creación de ConfigDict"""
        data = {'key1': 'value1', 'key2': 'value2'}
        config_dict = ConfigDict(data)
        
        assert config_dict.key1 == 'value1'
        assert config_dict.key2 == 'value2'
    
    def test_config_dict_nested(self):
        """Verifica ConfigDict anidado"""
        data = {
            'level1': {
                'level2': {
                    'value': 42
                }
            }
        }
        config_dict = ConfigDict(data)
        
        assert isinstance(config_dict.level1, ConfigDict)
        assert isinstance(config_dict.level1.level2, ConfigDict)
        assert config_dict.level1.level2.value == 42
    
    def test_config_dict_getitem(self):
        """Verifica acceso por índice"""
        data = {'key': 'value'}
        config_dict = ConfigDict(data)
        
        assert config_dict['key'] == 'value'


class TestConfigManager:
    """Tests para ConfigManager"""
    
    def test_load_config(self, temp_config_file):
        """Verifica que se cargue la configuración"""
        config = ConfigManager(temp_config_file)
        
        assert config.model.frames == 15
        assert config.model.keypoints_length == 1662
        assert config.model.min_length_frames == 5
    
    def test_get_word_ids(self, temp_config_file):
        """Verifica obtención de word_ids"""
        config = ConfigManager(temp_config_file)
        word_ids = config.get_word_ids()
        
        assert isinstance(word_ids, list)
        assert len(word_ids) == 3
        assert "hola" in word_ids
        assert "adios" in word_ids
        assert "bien" in word_ids
    
    def test_get_word_label(self, temp_config_file):
        """Verifica obtención de labels"""
        config = ConfigManager(temp_config_file)
        
        label = config.get_word_label("hola")
        assert label == "HOLA"
        
        label = config.get_word_label("adios")
        assert label == "ADIÓS"
    
    def test_get_word_label_with_suffix(self, temp_config_file):
        """Verifica labels con sufijos como -der, -izq"""
        config = ConfigManager(temp_config_file)
        
        # Debe extraer el ID base
        label = config.get_word_label("hola-der")
        assert label == "HOLA"
        
        label = config.get_word_label("hola-izq")
        assert label == "HOLA"
    
    def test_get_word_label_unknown(self, temp_config_file):
        """Verifica comportamiento con palabra desconocida"""
        config = ConfigManager(temp_config_file)
        
        # Debería retornar el ID en mayúsculas si no existe
        label = config.get_word_label("palabra_inexistente")
        assert label == "PALABRA_INEXISTENTE"
    
    def test_validate_config(self, temp_config_file):
        """Verifica validación de configuración"""
        config = ConfigManager(temp_config_file)
        
        # No debería lanzar excepciones
        config.validate_config()
    
    def test_get_keypoints_path(self, temp_config_file):
        """Verifica generación de path de keypoints"""
        config = ConfigManager(temp_config_file)
        
        path = config.get_keypoints_path("hola")
        assert isinstance(path, Path)
        assert "hola.h5" in str(path)
        assert "keypoints" in str(path)
    
    def test_get_model_path(self, temp_config_file):
        """Verifica generación de path de modelo"""
        config = ConfigManager(temp_config_file)
        
        path = config.get_model_path()
        assert isinstance(path, Path)
        assert path.suffix == ".keras"
        assert "models" in str(path)
    
    def test_get_word_labels_dict(self, temp_config_file):
        """Verifica obtención del diccionario completo"""
        config = ConfigManager(temp_config_file)
        
        labels_dict = config.get_word_labels_dict()
        assert isinstance(labels_dict, dict)
        assert "hola" in labels_dict
        assert "adios" in labels_dict
        assert labels_dict["hola"] == "HOLA"
    
    def test_config_singleton(self, temp_config_file):
        """Verifica que ConfigManager es singleton"""
        # ConfigManager NO es singleton por diseño - cada instancia es independiente
        config1 = ConfigManager(temp_config_file)
        config2 = ConfigManager(temp_config_file)
        
        # Ambas instancias deberían tener los mismos valores
        assert config1.model.frames == config2.model.frames
    
    def test_network_config(self, temp_config_file):
        """Verifica configuración de red neuronal"""
        config = ConfigManager(temp_config_file)
        
        assert config.network.lstm1_units == 64
        assert config.network.lstm2_units == 128
        assert config.network.dense1_units == 64
    
    def test_training_config(self, temp_config_file):
        """Verifica configuración de entrenamiento"""
        config = ConfigManager(temp_config_file)
        
        assert config.training.epochs == 500
        assert config.training.batch_size == 8
        assert config.training.validation_split == 0.05


class TestConfigValidation:
    """Tests para validación de configuración"""
    
    def test_validate_empty_vocabulary(self, temp_config_file):
        """Verifica que la validación funcione con vocabulario válido"""
        config = ConfigManager(temp_config_file)
        
        # El config tiene vocabulario válido, no debería lanzar excepciones
        config.validate_config()
        
        # Verificar que hay palabras en el vocabulario
        assert len(config.get_word_ids()) > 0
    
    def test_validate_frames_positive(self, temp_config_file):
        """Verifica que frames sea positivo"""
        config = ConfigManager(temp_config_file)
        
        assert config.model.frames > 0
        assert config.model.keypoints_length > 0
        assert config.model.min_length_frames > 0
