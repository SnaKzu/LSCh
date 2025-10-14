# 🧪 Guía de Testing para Proyecto LSP

## 📋 Índice

1. [Configuración de Git](#configuración-de-git)
2. [Estructura de Tests](#estructura-de-tests)
3. [Tests Unitarios](#tests-unitarios)
4. [Tests de Integración](#tests-de-integración)
5. [CI/CD con GitHub Actions](#cicd-con-github-actions)
6. [Pre-commit Hooks](#pre-commit-hooks)
7. [Comandos Útiles](#comandos-útiles)

---

## 🔧 Configuración de Git

### 1. Inicializar Repositorio

```powershell
# Navegar al proyecto
cd C:\Users\Diego\Documents\test6\modelo_lstm_lsp-main

# Inicializar Git
git init

# Configurar usuario (primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@ejemplo.com"

# Verificar configuración
git config --list
```

### 2. Crear .gitignore

Ejecuta:
```powershell
# Crear archivo .gitignore
New-Item -Path .gitignore -ItemType File
```

Contenido del `.gitignore`:
```gitignore
# ===================================================================
# GITIGNORE PARA PROYECTO LSP
# ===================================================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
.Python
env/
venv/
ENV/
.venv

# Jupyter Notebook
.ipynb_checkpoints

# PyCharm
.idea/

# VS Code
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# Datos y Modelos (NO SUBIR)
# Son archivos grandes que no deben estar en Git
data/
models/*.keras
models/*.h5
frame_actions/
*.hdf5

# Logs
logs/
*.log

# Archivos temporales
temp_pycache/
*.tmp
*.bak
*.swp
*~

# Sistema Operativo
.DS_Store
Thumbs.db
desktop.ini

# Archivos de configuración personal
config_local.yaml

# Pytest
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Archivos de test temporales
test_output/
test_frames/
```

### 3. Primer Commit

```powershell
# Ver estado
git status

# Agregar archivos
git add .

# Primer commit
git commit -m "Initial commit: Proyecto LSP refactorizado con TensorFlow 2.15"

# Ver historial
git log --oneline
```

### 4. Conectar con GitHub (Opcional)

```powershell
# Crear repositorio en GitHub primero, luego:
git remote add origin https://github.com/tu-usuario/proyecto-lsp.git
git branch -M main
git push -u origin main
```

---

## 🏗️ Estructura de Tests

### Crear Estructura de Carpetas

```powershell
# Crear carpetas de tests
New-Item -Path tests -ItemType Directory
New-Item -Path tests\unit -ItemType Directory
New-Item -Path tests\integration -ItemType Directory
New-Item -Path tests\fixtures -ItemType Directory
```

Estructura final:
```
modelo_lstm_lsp-main/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Configuración de pytest
│   ├── unit/                    # Tests unitarios
│   │   ├── __init__.py
│   │   ├── test_helpers.py
│   │   ├── test_config_manager.py
│   │   ├── test_model.py
│   │   └── test_evaluate_model.py
│   ├── integration/             # Tests de integración
│   │   ├── __init__.py
│   │   ├── test_pipeline.py
│   │   └── test_training.py
│   └── fixtures/                # Datos de prueba
│       ├── sample_frames/
│       └── test_config.yaml
```

---

## 🧪 Tests Unitarios

### 1. tests/__init__.py

```python
"""
Test suite para proyecto LSP
"""
```

### 2. tests/conftest.py

```python
"""
Configuración global de pytest
"""
import pytest
import sys
import os
from pathlib import Path
import numpy as np
import tempfile

# Agregar proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_mediapipe_results():
    """Mock de resultados de MediaPipe"""
    class MockLandmark:
        def __init__(self):
            self.x = 0.5
            self.y = 0.5
            self.z = 0.5
            self.visibility = 1.0
    
    class MockLandmarks:
        def __init__(self, count):
            self.landmark = [MockLandmark() for _ in range(count)]
    
    class MockResults:
        def __init__(self):
            self.pose_landmarks = MockLandmarks(33)
            self.face_landmarks = MockLandmarks(468)
            self.left_hand_landmarks = MockLandmarks(21)
            self.right_hand_landmarks = MockLandmarks(21)
    
    return MockResults()


@pytest.fixture
def sample_keypoints():
    """Genera keypoints de ejemplo"""
    # 1662 keypoints: pose(132) + face(1404) + left_hand(63) + right_hand(63)
    return np.random.rand(1662).astype(np.float32)


@pytest.fixture
def sample_keypoints_sequence():
    """Genera secuencia de keypoints de ejemplo"""
    # Secuencia de 15 frames
    return np.random.rand(15, 1662).astype(np.float32)


@pytest.fixture
def temp_config_file():
    """Crea un archivo de configuración temporal"""
    config_content = """
model:
  frames: 15
  keypoints_length: 1662
  min_length_frames: 7

vocabulary:
  word_ids:
    - "hola"
    - "adios"
  
  word_labels:
    hola: "HOLA"
    adios: "ADIÓS"

paths:
  frame_actions: "frame_actions"
  data: "data"
  models: "models"
  keypoints: "data/keypoints"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    
    yield temp_path
    
    # Limpieza
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def sample_image():
    """Genera una imagen de prueba"""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
```

### 3. tests/unit/test_helpers.py

```python
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
    mediapipe_detection
)


class TestExtractKeypoints:
    """Tests para extract_keypoints()"""
    
    def test_extract_keypoints_shape(self, mock_mediapipe_results):
        """Verifica que los keypoints tengan el shape correcto"""
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        assert keypoints.shape == (1662,)
        assert keypoints.dtype == np.float64 or keypoints.dtype == np.float32
    
    def test_extract_keypoints_without_pose(self, mock_mediapipe_results):
        """Verifica comportamiento sin pose landmarks"""
        mock_mediapipe_results.pose_landmarks = None
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        # Primeros 132 valores deben ser ceros
        assert np.all(keypoints[:132] == 0)
    
    def test_extract_keypoints_without_hands(self, mock_mediapipe_results):
        """Verifica comportamiento sin manos"""
        mock_mediapipe_results.left_hand_landmarks = None
        mock_mediapipe_results.right_hand_landmarks = None
        keypoints = extract_keypoints(mock_mediapipe_results)
        
        # Últimos 126 valores deben ser ceros (63 + 63)
        assert np.all(keypoints[-126:] == 0)


class TestCreateFolder:
    """Tests para create_folder()"""
    
    def test_create_folder_new(self, tmp_path):
        """Verifica creación de carpeta nueva"""
        test_path = tmp_path / "test_folder"
        create_folder(str(test_path))
        
        assert test_path.exists()
        assert test_path.is_dir()
    
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
        
        assert test_path.exists()
        assert test_path.is_dir()


class TestThereHand:
    """Tests para there_hand()"""
    
    def test_both_hands_present(self, mock_mediapipe_results):
        """Verifica detección con ambas manos"""
        assert there_hand(mock_mediapipe_results) is True
    
    def test_only_left_hand(self, mock_mediapipe_results):
        """Verifica detección solo con mano izquierda"""
        mock_mediapipe_results.right_hand_landmarks = None
        assert there_hand(mock_mediapipe_results) is True
    
    def test_only_right_hand(self, mock_mediapipe_results):
        """Verifica detección solo con mano derecha"""
        mock_mediapipe_results.left_hand_landmarks = None
        assert there_hand(mock_mediapipe_results) is True
    
    def test_no_hands(self, mock_mediapipe_results):
        """Verifica detección sin manos"""
        mock_mediapipe_results.left_hand_landmarks = None
        mock_mediapipe_results.right_hand_landmarks = None
        assert there_hand(mock_mediapipe_results) is False
```

### 4. tests/unit/test_config_manager.py

```python
"""
Tests unitarios para config_manager.py
"""
import pytest
from pathlib import Path

from config_manager import ConfigManager


class TestConfigManager:
    """Tests para ConfigManager"""
    
    def test_load_config(self, temp_config_file):
        """Verifica que se cargue la configuración"""
        config = ConfigManager(temp_config_file)
        
        assert config.model.frames == 15
        assert config.model.keypoints_length == 1662
    
    def test_get_word_ids(self, temp_config_file):
        """Verifica obtención de word_ids"""
        config = ConfigManager(temp_config_file)
        word_ids = config.get_word_ids()
        
        assert isinstance(word_ids, list)
        assert "hola" in word_ids
        assert "adios" in word_ids
    
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
```

### 5. tests/unit/test_evaluate_model.py

```python
"""
Tests unitarios para evaluate_model.py
"""
import pytest
import numpy as np

from evaluate_model import normalize_keypoints


class TestNormalizeKeypoints:
    """Tests para normalize_keypoints()"""
    
    def test_normalize_exact_length(self, sample_keypoints_sequence):
        """Verifica normalización con longitud exacta"""
        # Secuencia de 15 frames
        result = normalize_keypoints(sample_keypoints_sequence, target_frames=15)
        
        assert result.shape == (15, 1662)
        assert np.allclose(result, sample_keypoints_sequence)
    
    def test_normalize_shorter_sequence(self):
        """Verifica interpolación de secuencia corta"""
        # Secuencia de 10 frames -> 15 frames
        short_seq = np.random.rand(10, 1662).astype(np.float32)
        result = normalize_keypoints(short_seq, target_frames=15)
        
        assert result.shape == (15, 1662)
    
    def test_normalize_longer_sequence(self):
        """Verifica reducción de secuencia larga"""
        # Secuencia de 20 frames -> 15 frames
        long_seq = np.random.rand(20, 1662).astype(np.float32)
        result = normalize_keypoints(long_seq, target_frames=15)
        
        assert result.shape == (15, 1662)
    
    def test_normalize_preserves_keypoints_dimension(self):
        """Verifica que se preserven las 1662 dimensiones"""
        seq = np.random.rand(12, 1662).astype(np.float32)
        result = normalize_keypoints(seq, target_frames=15)
        
        assert result.shape[1] == 1662
```

---

## 🔗 Tests de Integración

### tests/integration/test_pipeline.py

```python
"""
Tests de integración del pipeline completo
"""
import pytest
import numpy as np
import tempfile
from pathlib import Path

from config_manager import config
from helpers import extract_keypoints, get_keypoints
from evaluate_model import normalize_keypoints


class TestPipeline:
    """Tests del pipeline completo"""
    
    def test_keypoints_to_normalized_sequence(self, mock_mediapipe_results):
        """Test: Keypoints -> Normalización"""
        # 1. Extraer keypoints
        kp_frame = extract_keypoints(mock_mediapipe_results)
        
        # 2. Crear secuencia
        sequence = np.array([kp_frame] * 12)  # 12 frames
        
        # 3. Normalizar
        normalized = normalize_keypoints(sequence, target_frames=15)
        
        assert normalized.shape == (15, 1662)
    
    def test_config_integration(self):
        """Verifica integración con configuración"""
        # Obtener valores de configuración
        frames = config.model.frames
        keypoints_len = config.model.keypoints_length
        
        # Crear secuencia con esos valores
        sequence = np.random.rand(frames, keypoints_len)
        
        assert sequence.shape == (frames, keypoints_len)
```

---

## 🚀 CI/CD con GitHub Actions

### .github/workflows/tests.yml

Crea la carpeta y archivo:

```powershell
New-Item -Path .github\workflows -ItemType Directory -Force
```

Contenido de `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~\AppData\Local\pip\Cache
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
    
    - name: Run unit tests
      run: |
        pytest tests/unit -v --cov=. --cov-report=xml --cov-report=html
    
    - name: Run integration tests
      run: |
        pytest tests/integration -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Archive test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.python-version }}
        path: htmlcov/
```

---

## 🪝 Pre-commit Hooks

### Instalar pre-commit

```powershell
pip install pre-commit
```

### .pre-commit-config.yaml

```yaml
repos:
  # Formateo de código
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3.10
  
  # Ordenar imports
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  # Linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--ignore=E203,W503']
  
  # Verificar archivos grandes
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
  
  # Tests antes de commit
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [tests/unit, -v]
```

### Activar pre-commit

```powershell
# Instalar hooks
pre-commit install

# Ejecutar manualmente en todos los archivos
pre-commit run --all-files
```

---

## 📝 pytest.ini

Configuración de pytest:

```ini
[pytest]
# Configuración de pytest para proyecto LSP

# Directorios de tests
testpaths = tests

# Patrones de archivos de test
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Opciones por defecto
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings

# Markers personalizados
markers =
    unit: Tests unitarios (fast)
    integration: Tests de integración (slow)
    slow: Tests lentos
    smoke: Tests de humo (básicos)

# Configuración de cobertura
[coverage:run]
source = .
omit =
    tests/*
    venv/*
    setup.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

## 🎯 Comandos Útiles

### Git

```powershell
# Ver estado
git status

# Ver cambios
git diff

# Agregar archivos específicos
git add helpers.py config_manager.py

# Commit con mensaje descriptivo
git commit -m "feat: Agregar sistema de logging"

# Ver historial
git log --oneline --graph

# Crear rama
git checkout -b feature/nueva-funcionalidad

# Cambiar de rama
git checkout main

# Merge de rama
git merge feature/nueva-funcionalidad

# Push
git push origin main

# Pull
git pull origin main

# Ver ramas
git branch -a
```

### Testing

```powershell
# Ejecutar TODOS los tests
pytest

# Tests unitarios solamente
pytest tests/unit

# Tests de integración solamente
pytest tests/integration

# Test específico
pytest tests/unit/test_helpers.py

# Con cobertura
pytest --cov=. --cov-report=html

# Modo verbose
pytest -v

# Parar en primer fallo
pytest -x

# Ejecutar tests marcados
pytest -m unit
pytest -m integration

# Ver print statements
pytest -s

# Ejecutar tests en paralelo
pytest -n auto
```

### Pre-commit

```powershell
# Instalar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files

# Ejecutar hook específico
pre-commit run black --all-files

# Actualizar hooks
pre-commit autoupdate

# Desinstalar
pre-commit uninstall
```

---

## 📊 Coverage Reports

### Generar reporte de cobertura

```powershell
# Generar reporte HTML
pytest --cov=. --cov-report=html

# Abrir reporte
start htmlcov\index.html

# Generar reporte XML (para CI/CD)
pytest --cov=. --cov-report=xml

# Ver reporte en consola
pytest --cov=. --cov-report=term
```

---

## 🎭 Ejemplo de Workflow Completo

### 1. Crear nueva funcionalidad

```powershell
# 1. Crear rama
git checkout -b feature/nueva-palabra

# 2. Hacer cambios
code helpers.py

# 3. Ejecutar tests
pytest tests/unit/test_helpers.py -v

# 4. Ver cobertura
pytest --cov=helpers --cov-report=term

# 5. Agregar tests para nuevo código
code tests/unit/test_helpers.py

# 6. Verificar que pasen todos los tests
pytest

# 7. Commit
git add helpers.py tests/unit/test_helpers.py
git commit -m "feat: Agregar función para nueva palabra"

# 8. Push
git push origin feature/nueva-palabra

# 9. Crear Pull Request en GitHub

# 10. Merge después de revisión
git checkout main
git pull origin main
git merge feature/nueva-palabra
```

---

## 📚 Recursos Adicionales

### Documentación

- **pytest**: https://docs.pytest.org/
- **coverage.py**: https://coverage.readthedocs.io/
- **pre-commit**: https://pre-commit.com/
- **Git**: https://git-scm.com/doc
- **GitHub Actions**: https://docs.github.com/en/actions

### Mejores Prácticas

1. **Escribe tests antes de código (TDD)**
2. **Un test por concepto**
3. **Nombres descriptivos**
4. **Tests independientes**
5. **Mock dependencias externas**
6. **Cobertura mínima 80%**
7. **Tests rápidos (<1s unitarios)**
8. **CI/CD en cada push**
9. **Commits atómicos**
10. **Mensajes de commit descriptivos**

---

## 🎊 ¡Siguiente Paso!

Ejecuta:

```powershell
# Crear estructura de tests
.\create_test_structure.ps1

# Ejecutar primer test
pytest tests/unit/test_helpers.py -v

# Inicializar Git
git init
git add .
git commit -m "Initial commit: LSP Project with tests"
```

**¡Tu proyecto ahora tiene tests profesionales!** 🚀
