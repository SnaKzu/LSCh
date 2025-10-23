"""
Minimal Flask app for Railway debugging
Simplified version without ML dependencies for initial deployment
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Basic Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'debug-key')

# Enable CORS
CORS(app)

@app.route('/')
def index():
    """Basic home page"""
    return jsonify({
        'message': 'LSCh Recognition API',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Minimal health check for Railway"""
    return jsonify({
        'status': 'ok',
        'service': 'lsch-recognition',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development'),
        'port': os.getenv('PORT', '5000')
    })

@app.route('/debug/env')
def debug_env():
    """Debug endpoint to see environment"""
    return jsonify({
        'environment_variables': {
            'PORT': os.getenv('PORT'),
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'SECRET_KEY': '***' if os.getenv('SECRET_KEY') else None,
            'DATABASE_URL': '***' if os.getenv('DATABASE_URL') else None,
        },
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'python_path': sys.path[:3]  # First 3 entries
    })

if __name__ == '__main__':
    print("=== LSCh Minimal App Starting ===")
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    print(f"Port: {port}")
    print(f"Debug: {debug_mode}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )