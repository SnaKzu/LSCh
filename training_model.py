"""
training_model.py - Entrenamiento del Modelo LSTM
==================================================

Script para entrenar el modelo de reconocimiento de señas LSP.
Actualizado para TensorFlow 2.15+ y usando configuración centralizada.
"""

import numpy as np
import logging
from pathlib import Path

# TensorFlow 2.15+ imports
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Imports del proyecto
from model import get_model
from helpers import get_word_ids, get_sequences_and_labels
from config_manager import config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def training_model(model_path: str = None, epochs: int = None, verbose: int = 1):
    """
    Entrena el modelo LSTM para clasificación de señas
    
    Args:
        model_path: Ruta donde guardar el modelo (default: desde config)
        epochs: Número máximo de épocas (default: desde config)
        verbose: Nivel de verbosidad (0, 1, 2)
    
    Returns:
        history: Historial del entrenamiento
    """
    # Usa valores de configuración si no se especifican
    if model_path is None:
        model_path = str(config.get_model_path())
    
    if epochs is None:
        epochs = config.training.epochs
    
    logger.info("=" * 70)
    logger.info("INICIANDO ENTRENAMIENTO DEL MODELO LSP")
    logger.info("=" * 70)
    logger.info(f"TensorFlow version: {tf.__version__}")
    logger.info(f"GPU disponible: {tf.config.list_physical_devices('GPU')}")
    
    # 1. Cargar IDs de palabras
    word_ids = config.get_word_ids()
    logger.info(f"\n📚 Vocabulario: {len(word_ids)} palabras")
    logger.info(f"Palabras: {', '.join(word_ids[:5])}{'...' if len(word_ids) > 5 else ''}")
    
    # 2. Cargar secuencias y etiquetas
    logger.info("\n📊 Cargando datos de entrenamiento...")
    sequences, labels = get_sequences_and_labels(word_ids)
    logger.info(f"Total de muestras: {len(sequences)}")
    
    if len(sequences) == 0:
        raise ValueError("No se encontraron datos de entrenamiento. Ejecute create_keypoints.py primero.")
    
    # 3. Padding/truncating de secuencias a tamaño fijo
    logger.info(f"\n⚙️  Normalizando secuencias a {config.model.frames} frames...")
    sequences = pad_sequences(
        sequences,
        maxlen=config.model.frames,
        padding='pre',
        truncating='post',
        dtype='float32'  # Cambiado de float16 a float32 para mejor precisión
    )
    
    # 4. Preparar datos
    X = np.array(sequences)
    y = to_categorical(labels, num_classes=len(word_ids)).astype(int)
    
    logger.info(f"Shape de X: {X.shape}")
    logger.info(f"Shape de y: {y.shape}")
    
    # 5. Split train/validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=config.training.validation_split,
        random_state=config.training.random_seed,
        stratify=labels  # Mantiene proporción de clases
    )
    
    logger.info(f"\n📈 División de datos:")
    logger.info(f"  Entrenamiento: {len(X_train)} muestras ({(1-config.training.validation_split)*100:.0f}%)")
    logger.info(f"  Validación: {len(X_val)} muestras ({config.training.validation_split*100:.0f}%)")
    
    # 6. Callbacks
    logger.info("\n🔧 Configurando callbacks...")
    
    callbacks = [
        # Early Stopping
        EarlyStopping(
            monitor='val_accuracy',
            patience=config.training.early_stopping_patience,
            restore_best_weights=True,
            verbose=1
        ),
        
        # Model Checkpoint - guarda mejor modelo
        ModelCheckpoint(
            filepath=model_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        
        # Reduce Learning Rate on Plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # 7. Construir modelo
    logger.info("\n🧠 Construyendo modelo...")
    model = get_model(config.model.frames, len(word_ids))
    
    if verbose >= 1:
        model.summary()
    
    # 8. Entrenar
    logger.info("\n🚀 Iniciando entrenamiento...")
    logger.info(f"Epochs máximos: {epochs}")
    logger.info(f"Batch size: {config.training.batch_size}")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=config.training.batch_size,
        callbacks=callbacks,
        verbose=verbose
    )
    
    # 9. Resultados finales
    logger.info("\n" + "=" * 70)
    logger.info("✓ ENTRENAMIENTO COMPLETADO")
    logger.info("=" * 70)
    
    # Mejor resultado
    best_epoch = np.argmax(history.history['val_accuracy']) + 1
    best_val_acc = max(history.history['val_accuracy'])
    best_train_acc = history.history['accuracy'][best_epoch - 1]
    
    logger.info(f"\n📊 Mejores resultados (época {best_epoch}):")
    logger.info(f"  Train Accuracy: {best_train_acc * 100:.2f}%")
    logger.info(f"  Val Accuracy: {best_val_acc * 100:.2f}%")
    logger.info(f"\n💾 Modelo guardado en: {model_path}")
    
    return history


if __name__ == "__main__":
    try:
        # Asegura que existan las carpetas necesarias
        config.create_directories()
        
        # Entrena el modelo
        history = training_model(verbose=2)
        
        logger.info("\n✅ Proceso completado exitosamente")
        logger.info("Siguiente paso: ejecute evaluate_model.py para probar el modelo")
        
    except Exception as e:
        logger.error(f"\n❌ Error durante el entrenamiento: {e}", exc_info=True)
        raise

    