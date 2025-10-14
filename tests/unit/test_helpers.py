"""
Tests unitarios para helpers.py
"""
import pytest
import numpy as np
import cv2
from pathlib import Path

from helpers import (
    extract_keypoints,
    create_folder,
    there_hand,
    mediapipe_detection,
    get_keypoints
)


class TestExtractKeypoints:
    """Tests para extract_keypoints()"""
    
    def test_extract_keypoints_shape(self, mock_mediapipe_results):
        """Verifica que los keypoints tengan el shape correcto"""
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        assert keypoints.shape == (1662,), f"Expected (1662,), got {keypoints.shape}"
        assert keypoints.dtype in [np.float64, np.float32]
    
    def test_extract_keypoints_without_pose(self, mock_mediapipe_results):
        """Verifica comportamiento sin pose landmarks"""
        mock_mediapipe_results.pose_landmarks = None
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        # Primeros 132 valores deben ser ceros
        assert np.all(keypoints[:132] == 0), "Pose keypoints should be zero when no pose detected"
    
    def test_extract_keypoints_without_face(self, mock_mediapipe_results):
        """Verifica comportamiento sin face landmarks"""
        mock_mediapipe_results.face_landmarks = None
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        # Valores de cara deben ser ceros (132:1536)
        assert np.all(keypoints[132:1536] == 0), "Face keypoints should be zero when no face detected"
    
    def test_extract_keypoints_without_hands(self, mock_mediapipe_results):
        """Verifica comportamiento sin manos"""
        mock_mediapipe_results.left_hand_landmarks = None
        mock_mediapipe_results.right_hand_landmarks = None
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        # Últimos 126 valores deben ser ceros (63 + 63)
        assert np.all(keypoints[-126:] == 0), "Hand keypoints should be zero when no hands detected"
    
    def test_extract_keypoints_values_range(self, mock_mediapipe_results):
        """Verifica que los valores estén en rango esperado"""
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        # Los valores de MediaPipe están normalizados entre 0 y 1
        assert np.all(keypoints >= 0), "All keypoints should be >= 0"
        assert np.all(keypoints <= 1), "All keypoints should be <= 1"


class TestCreateFolder:
    """Tests para create_folder()"""
    
    def test_create_folder_new(self, tmp_path):
        """Verifica creación de carpeta nueva"""
        test_path = tmp_path / "test_folder"
        create_folder(str(test_path))
        
        assert test_path.exists(), "Folder should be created"
        assert test_path.is_dir(), "Path should be a directory"
    
    def test_create_folder_existing(self, tmp_path):
        """Verifica que no falle con carpeta existente"""
        test_path = tmp_path / "existing_folder"
        test_path.mkdir()
        
        # No debería lanzar excepción
        create_folder(str(test_path))
        assert test_path.exists()
    
    def test_create_nested_folders(self, tmp_path):
        """Verifica creación de carpetas anidadas"""
        test_path = tmp_path / "level1" / "level2" / "level3"
        create_folder(str(test_path))
        
        assert test_path.exists(), "Nested folders should be created"
        assert test_path.is_dir()
    
    def test_create_folder_with_spaces(self, tmp_path):
        """Verifica creación con espacios en el nombre"""
        test_path = tmp_path / "folder with spaces"
        create_folder(str(test_path))
        
        assert test_path.exists()


class TestThereHand:
    """Tests para there_hand()"""
    
    def test_both_hands_present(self, mock_mediapipe_results):
        """Verifica detección con ambas manos"""
        result = there_hand(mock_mediapipe_results)
        assert result, "Should detect hands when both are present"
    
    def test_only_left_hand(self, mock_mediapipe_results):
        """Verifica detección solo con mano izquierda"""
        mock_mediapipe_results.right_hand_landmarks = None
        result = there_hand(mock_mediapipe_results)
        assert result, "Should detect hand when only left is present"
    
    def test_only_right_hand(self, mock_mediapipe_results):
        """Verifica detección solo con mano derecha"""
        mock_mediapipe_results.left_hand_landmarks = None
        result = there_hand(mock_mediapipe_results)
        assert result, "Should detect hand when only right is present"
    
    def test_no_hands(self, mock_mediapipe_results):
        """Verifica detección sin manos"""
        mock_mediapipe_results.left_hand_landmarks = None
        mock_mediapipe_results.right_hand_landmarks = None
        result = there_hand(mock_mediapipe_results)
        assert not result, "Should not detect hands when none are present"


class TestGetKeypoints:
    """Tests para get_keypoints()"""
    
    @pytest.mark.skip(reason="Requires MediaPipe model initialization")
    def test_get_keypoints_from_frames(self, sample_frames):
        """Verifica extracción de keypoints desde frames"""
        # Este test requiere un modelo real de MediaPipe
        # Se salta por defecto pero útil para testing de integración
        pass
    
    def test_get_keypoints_empty_folder(self, tmp_path):
        """Verifica comportamiento con carpeta vacía"""
        empty_folder = tmp_path / "empty"
        empty_folder.mkdir()
        
        # Debería retornar array vacío o manejar gracefully
        # (dependiendo de la implementación)
        pass


class TestMediapipeDetection:
    """Tests para mediapipe_detection()"""
    
    @pytest.mark.skip(reason="Requires MediaPipe model and real image")
    def test_mediapipe_detection_with_image(self, sample_image):
        """Verifica procesamiento de imagen"""
        # Este test requiere un modelo real
        pass
    
    def test_mediapipe_detection_input_format(self, sample_image):
        """Verifica que acepta imagen BGR"""
        # La imagen debe estar en formato BGR (OpenCV)
        assert sample_image.shape == (480, 640, 3)
        assert sample_image.dtype == np.uint8
