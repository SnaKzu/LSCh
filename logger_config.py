"""
logger_config.py - Sistema de Logging Centralizado
===================================================

Configuración unificada de logging para todo el proyecto LSP.
Facilita debugging y seguimiento de errores.

Características:
- Logs en consola y archivo
- Diferentes niveles por módulo
- Rotación automática de archivos
- Formato consistente con timestamps
- Colores en consola (opcional)

Uso:
    from logger_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("Mensaje informativo")
    logger.debug("Información de debug")
    logger.warning("Advertencia")
    logger.error("Error")
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


# Configuración de colores para consola (Windows compatible)
class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agrega color al nivel
        if sys.stdout.isatty():  # Solo si es terminal interactivo
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    log_level=logging.INFO,
    log_file=None,
    console_output=True,
    file_output=True,
    colored=True
):
    """
    Configura el sistema de logging global
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log (default: logs/lsp_{fecha}.log)
        console_output: Si True, muestra logs en consola
        file_output: Si True, guarda logs en archivo
        colored: Si True, usa colores en consola
    
    Returns:
        Logger raíz configurado
    """
    # Crear directorio de logs si no existe
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo de log
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"lsp_{timestamp}.log"
    else:
        log_file = log_dir / log_file
    
    # Formato de los mensajes
    log_format = "%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        if colored:
            console_formatter = ColoredFormatter(log_format, date_format)
        else:
            console_formatter = logging.Formatter(log_format, date_format)
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Handler para archivo con rotación
    if file_output:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Archivo guarda todo
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Log inicial
    root_logger.info("=" * 70)
    root_logger.info("Sistema de Logging Inicializado")
    root_logger.info(f"Nivel: {logging.getLevelName(log_level)}")
    if file_output:
        root_logger.info(f"Archivo: {log_file}")
    root_logger.info("=" * 70)
    
    return root_logger


def get_logger(name: str, level=None):
    """
    Obtiene un logger para un módulo específico
    
    Args:
        name: Nombre del módulo (__name__)
        level: Nivel de logging específico (opcional)
    
    Returns:
        Logger configurado
    
    Ejemplo:
        logger = get_logger(__name__)
        logger.info("Iniciando proceso...")
    """
    logger = logging.getLogger(name)
    
    if level is not None:
        logger.setLevel(level)
    
    return logger


def set_log_level(level):
    """
    Cambia el nivel de logging global
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              o string: "DEBUG", "INFO", etc.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(level)
    
    logging.info(f"Nivel de logging cambiado a: {logging.getLevelName(level)}")


def log_function_call(func):
    """
    Decorador para loggear llamadas a funciones
    
    Uso:
        @log_function_call
        def mi_funcion(param1, param2):
            pass
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"→ Llamando {func.__name__}(args={args}, kwargs={kwargs})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← {func.__name__} completado exitosamente")
            return result
        except Exception as e:
            logger.error(f"✗ {func.__name__} falló: {e}", exc_info=True)
            raise
    
    return wrapper


def log_execution_time(func):
    """
    Decorador para medir y loggear tiempo de ejecución
    
    Uso:
        @log_execution_time
        def proceso_lento():
            pass
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        elapsed_time = time.time() - start_time
        logger.info(f"⏱️  {func.__name__} ejecutado en {elapsed_time:.2f}s")
        
        return result
    
    return wrapper


# Inicialización automática al importar
_initialized = False

def ensure_logging_initialized():
    """Asegura que el logging esté inicializado"""
    global _initialized
    
    if not _initialized:
        # Configuración por defecto
        setup_logging(
            log_level=logging.INFO,
            console_output=True,
            file_output=True,
            colored=True
        )
        _initialized = True


# Inicializar al importar el módulo
ensure_logging_initialized()


if __name__ == "__main__":
    # Testing del sistema de logging
    print("=" * 70)
    print("TESTING SISTEMA DE LOGGING")
    print("=" * 70)
    print()
    
    # Crear logger de prueba
    logger = get_logger("test_module")
    
    # Probar diferentes niveles
    logger.debug("🐛 Mensaje de DEBUG - Información detallada")
    logger.info("ℹ️  Mensaje de INFO - Información general")
    logger.warning("⚠️  Mensaje de WARNING - Advertencia")
    logger.error("❌ Mensaje de ERROR - Error recuperable")
    
    # Probar decoradores
    @log_function_call
    @log_execution_time
    def funcion_prueba(a, b):
        """Función de prueba"""
        import time
        time.sleep(0.5)
        return a + b
    
    print()
    resultado = funcion_prueba(2, 3)
    print(f"\nResultado: {resultado}")
    
    # Cambiar nivel de logging
    print()
    print("Cambiando a nivel DEBUG...")
    set_log_level("DEBUG")
    
    logger.debug("🐛 Ahora este mensaje DEBUG es visible")
    
    print()
    print("=" * 70)
    print("✓ Testing completado")
    print(f"✓ Logs guardados en: {Path(__file__).parent / 'logs'}")
    print("=" * 70)
