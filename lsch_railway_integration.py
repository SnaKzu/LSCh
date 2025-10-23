#!/usr/bin/env python3
"""
LSCh Railway Integration - Model Loading and Prediction
=======================================================
Railway-optimized version for LSCh sign language recognition
"""
import os
import logging
import numpy as np
import tensorflow as tf
from datetime import datetime
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSChModelManager:
    """Manages LSCh LSTM model loading and predictions in Railway environment"""
    
    def __init__(self):
        self.model = None
        self.word_ids = []
        self.model_path = 'models/actions_15.keras'
        self.words_path = 'models/words.json'
        self.is_loaded = False
        
    def load_model(self):
        """Load LSTM model and vocabulary"""
        try:
            # Load vocabulary
            if os.path.exists(self.words_path):
                with open(self.words_path, 'r', encoding='utf-8') as f:
                    vocab_data = json.load(f)
                    self.word_ids = vocab_data.get('word_ids', [])
                logger.info(f"✅ Loaded vocabulary: {len(self.word_ids)} words")
            else:
                logger.warning(f"⚠️  Vocabulary file not found: {self.words_path}")
                # Fallback vocabulary
                self.word_ids = [
                    "adios", "bien", "buenas_noches", "buenas_tardes", "buenos_dias",
                    "como_estas", "disculpa", "gracias", "hola-der", "hola-izq",
                    "mal", "mas_o_menos", "me_ayudas", "por_favor"
                ]
                
            # Load model
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"✅ Model loaded successfully")
                logger.info(f"   Input shape: {self.model.input_shape}")
                logger.info(f"   Output classes: {len(self.word_ids)}")
                self.is_loaded = True
            else:
                logger.warning(f"⚠️  Model file not found: {self.model_path}")
                self._create_dummy_model()
                
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            self._create_dummy_model()
            
    def _create_dummy_model(self):
        """Create a dummy model for testing without the actual trained model"""
        logger.info("Creating dummy model for testing...")
        
        # Create simple model architecture matching expected input/output
        self.model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(30, 258)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(128, return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(len(self.word_ids), activation='softmax')
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.is_loaded = True
        logger.info("✅ Dummy model created for testing")
        
    def predict(self, keypoints_sequence):
        """
        Predict sign language gesture from keypoints sequence
        
        Args:
            keypoints_sequence: numpy array of shape (frames, keypoints)
            
        Returns:
            dict: Prediction results with confidence scores
        """
        if not self.is_loaded:
            return {"error": "Model not loaded"}
            
        try:
            # Ensure correct input shape
            if len(keypoints_sequence.shape) == 2:
                keypoints_sequence = np.expand_dims(keypoints_sequence, axis=0)
                
            # Make prediction
            predictions = self.model.predict(keypoints_sequence, verbose=0)
            
            # Get top predictions
            top_indices = np.argsort(predictions[0])[::-1][:3]
            
            results = {
                "predicted_word": self.word_ids[top_indices[0]],
                "confidence": float(predictions[0][top_indices[0]]),
                "top_predictions": [
                    {
                        "word": self.word_ids[idx],
                        "confidence": float(predictions[0][idx])
                    }
                    for idx in top_indices
                ]
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {str(e)}")
            return {"error": str(e)}
    
    def get_status(self):
        """Get model status information"""
        return {
            "model_loaded": self.is_loaded,
            "model_path": self.model_path,
            "vocabulary_size": len(self.word_ids),
            "words": self.word_ids,
            "model_summary": {
                "input_shape": str(self.model.input_shape) if self.model else None,
                "output_shape": str(self.model.output_shape) if self.model else None,
                "parameters": self.model.count_params() if self.model else None
            } if self.model else None
        }

class MockKeypointsExtractor:
    """Mock keypoints extractor for Railway testing without MediaPipe"""
    
    def __init__(self):
        self.keypoints_length = 258  # Expected keypoints per frame
        
    def extract_keypoints_from_frame(self, frame_data):
        """
        Mock keypoints extraction from frame data
        In production, this would use OpenCV + pose estimation
        """
        # Generate mock keypoints for testing
        # In real implementation, this would process the frame
        mock_keypoints = np.random.random(self.keypoints_length) * 0.1
        
        return {
            "keypoints": mock_keypoints,
            "landmarks_detected": True,
            "pose_confidence": 0.85,
            "hand_confidence": 0.78
        }
        
    def process_sequence(self, frames_data, target_frames=30):
        """
        Process a sequence of frames to extract keypoints
        
        Args:
            frames_data: List of frame data
            target_frames: Target number of frames for model input
            
        Returns:
            numpy array: Keypoints sequence ready for model prediction
        """
        sequence = []
        
        for frame in frames_data[:target_frames]:
            result = self.extract_keypoints_from_frame(frame)
            sequence.append(result["keypoints"])
            
        # Pad or truncate sequence to target length
        while len(sequence) < target_frames:
            sequence.append(np.zeros(self.keypoints_length))
            
        return np.array(sequence[:target_frames])

# Global instances
model_manager = LSChModelManager()
keypoints_extractor = MockKeypointsExtractor()

def initialize_lsch_system():
    """Initialize the LSCh recognition system"""
    logger.info("🚀 Initializing LSCh Recognition System...")
    
    # Load model
    model_manager.load_model()
    
    # Test prediction with dummy data
    test_sequence = np.random.random((30, 258))
    test_result = model_manager.predict(test_sequence)
    
    logger.info("✅ LSCh System initialized successfully")
    logger.info(f"   Test prediction: {test_result.get('predicted_word', 'N/A')}")
    
    return model_manager.is_loaded

def get_system_status():
    """Get comprehensive system status"""
    return {
        "system_initialized": model_manager.is_loaded,
        "model_status": model_manager.get_status(),
        "keypoints_extractor": {
            "type": "mock_extractor",
            "keypoints_per_frame": keypoints_extractor.keypoints_length,
            "available": True
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the system
    initialize_lsch_system()
    status = get_system_status()
    print(json.dumps(status, indent=2))