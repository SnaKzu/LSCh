"""
Modelos de base de datos para LSP Web Application
Usuario y sesiones
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Modelo de usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relación con predicciones
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hashear password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Actualizar último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Modelo de predicción (historial)"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word = db.Column(db.String(50), nullable=False)
    word_id = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    session_id = db.Column(db.String(100))
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'word': self.word,
            'word_id': self.word_id,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id
        }
    
    def __repr__(self):
        return f'<Prediction {self.word} ({self.confidence:.2%})>'
