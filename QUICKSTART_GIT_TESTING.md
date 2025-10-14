# 🚀 Inicio Rápido - Git & Testing

## 📦 Instalación de Herramientas

```powershell
# 1. Instalar pytest y herramientas de testing
py -3.10 -m pip install pytest pytest-cov pytest-mock --user

# 2. Verificar instalación
pytest --version
```

## 🎯 Comandos Esenciales

### Git - Primeros Pasos

```powershell
# 1. Inicializar repositorio
git init

# 2. Configurar usuario (primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# 3. Ver estado
git status

# 4. Agregar archivos
git add .

# 5. Primer commit
git commit -m "Initial commit: LSP Project refactorizado"

# 6. Ver historial
git log --oneline
```

### Testing - Comandos Básicos

```powershell
# 1. Crear estructura de tests
.\create_test_structure.ps1

# 2. Ejecutar todos los tests
pytest

# 3. Ejecutar tests unitarios
pytest tests/unit -v

# 4. Ver cobertura
pytest --cov=. --cov-report=html

# 5. Abrir reporte de cobertura
start htmlcov\index.html
```

## 📝 Workflow Diario

### 1. Antes de Empezar a Trabajar

```powershell
# Actualizar desde repositorio
git pull origin main

# Crear rama para nueva funcionalidad
git checkout -b feature/mi-funcionalidad
```

### 2. Durante el Desarrollo

```powershell
# Ejecutar tests continuamente
pytest tests/unit -v

# Verificar cambios
git status
git diff

# Agregar archivos modificados
git add archivo1.py archivo2.py

# Commit con mensaje descriptivo
git commit -m "feat: Agregar nueva funcionalidad X"
```

### 3. Antes de Hacer Push

```powershell
# Ejecutar TODOS los tests
pytest

# Verificar cobertura
pytest --cov=. --cov-report=term

# Push a tu rama
git push origin feature/mi-funcionalidad
```

## 🎨 Convención de Commits

```
feat: Nueva funcionalidad
fix: Corrección de bug
docs: Cambios en documentación
test: Agregar o modificar tests
refactor: Refactorización de código
style: Formato de código
perf: Mejora de performance
chore: Tareas de mantenimiento
```

### Ejemplos:

```powershell
git commit -m "feat: Agregar soporte para nueva palabra 'gracias'"
git commit -m "fix: Corregir detección de manos en lighting bajo"
git commit -m "docs: Actualizar TESTING_GUIDE.md"
git commit -m "test: Agregar tests para normalize_keypoints"
git commit -m "refactor: Mejorar performance de extract_keypoints"
```

## ✅ Checklist Antes de Commit

- [ ] ✅ Tests pasan: `pytest`
- [ ] ✅ Código formateado correctamente
- [ ] ✅ Sin archivos grandes (modelos, datos)
- [ ] ✅ `.gitignore` actualizado si es necesario
- [ ] ✅ Commit message descriptivo
- [ ] ✅ Sin credenciales o datos sensibles

## 🔍 Comandos Útiles

### Git

```powershell
# Ver cambios específicos
git diff helpers.py

# Ver historial de un archivo
git log --follow helpers.py

# Deshacer cambios no commiteados
git checkout -- archivo.py

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Ver ramas
git branch -a

# Cambiar de rama
git checkout main

# Ver quién modificó cada línea
git blame helpers.py
```

### Testing

```powershell
# Test específico
pytest tests/unit/test_helpers.py::TestExtractKeypoints::test_extract_keypoints_shape

# Solo tests rápidos
pytest -m unit

# Parar en primer error
pytest -x

# Modo verbose con prints
pytest -v -s

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Ver tests disponibles sin ejecutar
pytest --collect-only
```

## 📊 Verificar Cobertura de Tests

```powershell
# Generar reporte de cobertura
pytest --cov=. --cov-report=html --cov-report=term

# Ver cobertura por módulo
pytest --cov=helpers --cov-report=term

# Ver líneas no cubiertas
pytest --cov=helpers --cov-report=term-missing
```

## 🐛 Debugging de Tests

```powershell
# Ver output completo
pytest -s

# Entrar en debugger al fallar
pytest --pdb

# Ver traceback completo
pytest --tb=long

# Solo últimas líneas de error
pytest --tb=short
```

## 📚 Recursos Rápidos

- **TESTING_GUIDE.md** - Guía completa de testing
- **pytest.ini** - Configuración de pytest
- **tests/conftest.py** - Fixtures compartidas
- **.gitignore** - Archivos ignorados por Git

## 🎊 Tu Primer Test

### 1. Crear el test

```python
# tests/unit/test_mi_modulo.py
def test_mi_funcion():
    from mi_modulo import mi_funcion
    
    resultado = mi_funcion(42)
    
    assert resultado == 42
```

### 2. Ejecutar el test

```powershell
pytest tests/unit/test_mi_modulo.py -v
```

### 3. Commit del test

```powershell
git add tests/unit/test_mi_modulo.py
git commit -m "test: Agregar test para mi_funcion"
```

## 🚀 ¡Listo!

Ahora tienes todo configurado para:
- ✅ Control de versiones con Git
- ✅ Testing automatizado con pytest
- ✅ Cobertura de código
- ✅ Workflow profesional

**Próximo paso:**
```powershell
pytest tests/unit -v
```

¡Deberías ver todos los tests en verde! 🎉
