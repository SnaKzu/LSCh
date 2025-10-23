"""
Intermediate Flask app for Railway - ML libraries test
Testing ML imports without heavy model loading
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Test ML imports
ml_status = {}

try:
    import numpy as np
    ml_status['numpy'] = f"OK - {np.__version__}"
except Exception as e:
    ml_status['numpy'] = f"ERROR - {str(e)}"

try:
    import pandas as pd
    ml_status['pandas'] = f"OK - {pd.__version__}"
except Exception as e:
    ml_status['pandas'] = f"ERROR - {str(e)}"

try:
    import cv2
    ml_status['opencv'] = f"OK - {cv2.__version__}"
except Exception as e:
    ml_status['opencv'] = f"ERROR - {str(e)}"

try:
    import mediapipe as mp
    ml_status['mediapipe'] = f"OK - {mp.__version__}"
except Exception as e:
    ml_status['mediapipe'] = f"ERROR - {str(e)}"

try:
    import tensorflow as tf
    ml_status['tensorflow'] = f"OK - {tf.__version__}"
except Exception as e:
    ml_status['tensorflow'] = f"ERROR - {str(e)}"

# Basic Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'debug-key')
CORS(app)

@app.route('/')
def index():
    """Basic home page with ML status"""
    return jsonify({
        'message': 'LSCh Recognition API - ML Testing',
        'status': 'running',
        'ml_libraries': ml_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Health check for Railway"""
    return jsonify({
        'status': 'ok',
        'service': 'lsch-recognition-ml-test',
        'ml_imports': ml_status,
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/api/ml-test')
def ml_test():
    """Test ML operations"""
    tests = {}
    
    try:
        # NumPy test
        arr = np.array([1, 2, 3])
        tests['numpy_operation'] = f"OK - array: {arr.tolist()}"
    except Exception as e:
        tests['numpy_operation'] = f"ERROR - {str(e)}"
    
    try:
        # TensorFlow basic test (no model loading)
        import tensorflow as tf
        tf_version = tf.__version__
        tests['tensorflow_basic'] = f"OK - version: {tf_version}"
        
        # Simple TF operation
        x = tf.constant([1, 2, 3])
        tests['tensorflow_operation'] = f"OK - constant: {x.numpy().tolist()}"
    except Exception as e:
        tests['tensorflow_operation'] = f"ERROR - {str(e)}"
    
    try:
        # MediaPipe basic test (no model init)
        import mediapipe as mp
        mp_version = mp.__version__
        tests['mediapipe_basic'] = f"OK - version: {mp_version}"
    except Exception as e:
        tests['mediapipe_basic'] = f"ERROR - {str(e)}"
    
    return jsonify({
        'ml_tests': tests,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=== LSCh ML Testing App Starting ===")
    print("ML Library Status:")
    for lib, status in ml_status.items():
        print(f"  {lib}: {status}")
    
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    print(f"Port: {port}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )