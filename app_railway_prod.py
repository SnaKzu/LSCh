#!/usr/bin/env python3
"""
LSCh Railway Production App - Optimized for headless environment
"""
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all required libraries for Railway deployment"""
    status = {}
    
    # Test core libraries
    try:
        import numpy as np
        status['numpy'] = f"OK - {np.__version__}"
        logger.info(f"✅ numpy: {np.__version__}")
    except Exception as e:
        status['numpy'] = f"ERROR - {str(e)}"
        logger.error(f"❌ numpy: {str(e)}")
    
    try:
        import pandas as pd
        status['pandas'] = f"OK - {pd.__version__}"
        logger.info(f"✅ pandas: {pd.__version__}")
    except Exception as e:
        status['pandas'] = f"ERROR - {str(e)}"
        logger.error(f"❌ pandas: {str(e)}")
    
    # Test OpenCV headless
    try:
        import cv2
        status['opencv'] = f"OK - {cv2.__version__}"
        logger.info(f"✅ opencv-headless: {cv2.__version__}")
        
        # Test basic opencv operations
        import numpy as np
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        status['opencv_operations'] = "OK - Basic operations working"
        logger.info("✅ OpenCV operations: Working")
        
    except Exception as e:
        status['opencv'] = f"ERROR - {str(e)}"
        logger.error(f"❌ opencv: {str(e)}")
    
    # Test TensorFlow
    try:
        import tensorflow as tf
        status['tensorflow'] = f"OK - {tf.__version__}"
        logger.info(f"✅ tensorflow: {tf.__version__}")
        
        # Test basic TensorFlow operations
        x = tf.constant([1, 2, 3])
        y = tf.constant([4, 5, 6])
        z = tf.add(x, y)
        status['tensorflow_operations'] = f"OK - Basic ops: {z.numpy()}"
        logger.info("✅ TensorFlow operations: Working")
        
    except Exception as e:
        status['tensorflow'] = f"ERROR - {str(e)}"
        logger.error(f"❌ tensorflow: {str(e)}")
    
    # Skip MediaPipe for now - causes GUI issues
    status['mediapipe'] = "SKIPPED - GUI dependency issues in Railway"
    logger.info("⚠️  MediaPipe: Skipped (GUI issues)")
    
    return status

def create_app():
    """Create Flask app with Railway-optimized configuration"""
    app = Flask(__name__)
    
    # Railway-specific configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
    
    # Enable CORS
    CORS(app, origins="*")
    
    print("=== LSCh Railway Production App Starting ===")
    
    # Test imports at startup
    ml_status = test_imports()
    print("ML Library Status:")
    for lib, status in ml_status.items():
        print(f"  {lib}: {status}")
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "LSCh Railway Production API",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "environment": app.config['ENV']
        })
    
    @app.route('/api/health')
    def health():
        """Health check endpoint for Railway"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": app.config['ENV']
        }), 200
    
    @app.route('/api/ml-status')
    def ml_status_endpoint():
        """Detailed ML libraries status"""
        status = test_imports()
        return jsonify({
            "ml_libraries": status,
            "timestamp": datetime.now().isoformat(),
            "railway_optimized": True
        })
    
    @app.route('/api/cv-test')
    def cv_test():
        """Test computer vision capabilities without MediaPipe"""
        try:
            import cv2
            import numpy as np
            
            # Create test image
            img = np.zeros((200, 200, 3), dtype=np.uint8)
            
            # Test basic OpenCV operations
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (15, 15), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            return jsonify({
                "opencv_test": "success",
                "operations": {
                    "color_conversion": "OK",
                    "gaussian_blur": "OK", 
                    "edge_detection": "OK"
                },
                "image_shapes": {
                    "original": img.shape,
                    "grayscale": gray.shape,
                    "edges": edges.shape
                }
            })
        except Exception as e:
            return jsonify({
                "opencv_test": "failed",
                "error": str(e)
            }), 500
    
    @app.route('/api/tf-test')
    def tf_test():
        """Test TensorFlow model creation"""
        try:
            import tensorflow as tf
            import numpy as np
            
            # Create simple model
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(10, activation='relu', input_shape=(8,)),
                tf.keras.layers.Dense(5, activation='softmax')
            ])
            
            # Test prediction
            test_data = np.random.random((1, 8))
            prediction = model.predict(test_data, verbose=0)
            
            return jsonify({
                "tensorflow_test": "success",
                "model_summary": {
                    "layers": len(model.layers),
                    "params": model.count_params(),
                    "input_shape": str(model.input_shape),
                    "output_shape": str(model.output_shape)
                },
                "prediction_shape": prediction.shape,
                "prediction_sample": prediction[0][:3].tolist()
            })
        except Exception as e:
            return jsonify({
                "tensorflow_test": "failed", 
                "error": str(e)
            }), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Port: {port}")
    print(f"Environment: {app.config['ENV']}")
    
    if app.config['ENV'] == 'production':
        # Production mode - let Railway handle this
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode
        app.run(host='127.0.0.1', port=port, debug=True)