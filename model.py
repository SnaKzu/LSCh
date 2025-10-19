"""
model.py - Arquitectura de la Red Neuronal LSTM
================================================

Define la arquitectura del modelo LSTM para clasificación de señas.
Actualizado para TensorFlow 2.15+ y usando configuración centralizada.
"""

import tensorflow as tf
from tensorflow import keras
# Avoid importing tensorflow.keras.models directly to prevent unresolved import errors in some environments;
# use keras.Sequential (available from "from tensorflow import keras") when instantiating the model.
# Reference layers and regularizers from the already-imported `keras` to avoid unresolved import issues in some editors.
LSTM = keras.layers.LSTM
Dense = keras.layers.Dense
Dropout = keras.layers.Dropout
l2 = keras.regularizers.l2
import logging

# Importa configuración centralizada
from config_manager import config

logger = logging.getLogger(__name__)


def get_model(max_length_frames: int = None, output_length: int = None):
    """
    Construye el modelo LSTM para clasificación de señas
    
    Args:
        max_length_frames: Número de frames en cada secuencia (default: desde config)
        output_length: Número de clases a predecir (default: desde vocabulario en config)
    
    Returns:
        keras.Model: Modelo compilado listo para entrenar
    """
    # Usa valores de configuración si no se especifican
    if max_length_frames is None:
        max_length_frames = config.model.frames
    
    if output_length is None:
        output_length = len(config.get_word_ids())
    
    # Obtiene configuración de red desde config.yaml
    net_config = config.network
    
    logger.info(f"Construyendo modelo LSTM:")
    logger.info(f"  Input shape: ({max_length_frames}, {config.model.keypoints_length})")
    logger.info(f"  Output classes: {output_length}")
    # Construcción del modelo
    model = keras.Sequential(name='LSP_LSTM_Classifier')
    
    # Primera capa LSTM con return_sequences=True
    model.add(LSTM(
        units=net_config.lstm1_units,
        return_sequences=True,
        input_shape=(max_length_frames, config.model.keypoints_length),
        kernel_regularizer=l2(net_config.lstm1_l2),
        name='lstm_layer_1'
    ))
    model.add(Dropout(net_config.lstm1_dropout, name='dropout_1'))
    
    # Segunda capa LSTM con return_sequences=False
    model.add(LSTM(
        units=net_config.lstm2_units,
        return_sequences=False,
        kernel_regularizer=l2(net_config.lstm2_l2),
        name='lstm_layer_2'
    ))
    model.add(Dropout(net_config.lstm2_dropout, name='dropout_2'))
    
    # Capas densas
    model.add(Dense(
        units=net_config.dense1_units,
        activation='relu',
        kernel_regularizer=l2(net_config.dense1_l2),
        name='dense_layer_1'
    ))
    
    model.add(Dense(
        units=net_config.dense2_units,
        activation='relu',
        kernel_regularizer=l2(net_config.dense2_l2),
        name='dense_layer_2'
    ))
    
    # Capa de salida con softmax
    model.add(Dense(
        units=output_length,
        activation='softmax',
        name='output_layer'
    ))
    
    # Compilación del modelo
    model.compile(
        optimizer=net_config.optimizer,
        loss=net_config.loss,
        metrics=net_config.metrics
    )
    
    logger.info("✓ Modelo construido y compilado exitosamente")
    
    return model


def get_model_summary(max_length_frames: int = None, output_length: int = None) -> str:
    """
    Retorna un resumen del modelo en string
    
    Args:
        max_length_frames: Número de frames en cada secuencia
        output_length: Número de clases a predecir
    
    Returns:
        str: Resumen del modelo
    """
    model = get_model(max_length_frames, output_length)
    
    # Captura el summary en un string
    import io
    stream = io.StringIO()
    model.summary(print_fn=lambda x: stream.write(x + '\n'))
    summary_str = stream.getvalue()
    stream.close()
    
    return summary_str


if __name__ == "__main__":
    # Configurar logging para testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    print("=" * 70)
    print("ARQUITECTURA DEL MODELO LSTM")
    print("=" * 70)
    
    # Construye el modelo con valores por defecto
    model = get_model()
    
    # Muestra resumen
    print("\n")
    model.summary()
    
    print("\n" + "=" * 70)
    print(f"Total de parámetros: {model.count_params():,}")
    print("=" * 70)
    
    # Información adicional
    print(f"\n📊 Configuración:")
    print(f"  - Optimizer: {config.network.optimizer}")
    print(f"  - Loss: {config.network.loss}")
    print(f"  - Metrics: {config.network.metrics}")
    print(f"\n✓ Modelo compatible con TensorFlow {tf.__version__}")
