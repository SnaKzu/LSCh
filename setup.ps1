# ===================================================================
# Script de Setup Automático - Proyecto LSP
# ===================================================================
# Descripción: Configura el entorno virtual e instala dependencias
# Uso: .\setup.ps1
# ===================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP PROYECTO LSP - Traductor LSP   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/6] Verificando versión de Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Green

if ($pythonVersion -notmatch "Python 3\.(10|11|12)") {
    Write-Host "  ⚠️  ADVERTENCIA: Se recomienda Python 3.10, 3.11 o 3.12" -ForegroundColor Red
    Write-Host "  Versión detectada: $pythonVersion" -ForegroundColor Red
    $continue = Read-Host "¿Continuar de todos modos? (s/n)"
    if ($continue -ne "s") {
        exit 1
    }
}

# 2. Crear entorno virtual
Write-Host ""
Write-Host "[2/6] Creando entorno virtual..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "  ℹ️  Entorno virtual ya existe. ¿Desea recrearlo?" -ForegroundColor Cyan
    $recreate = Read-Host "  (s/n)"
    if ($recreate -eq "s") {
        Write-Host "  Eliminando entorno virtual antiguo..." -ForegroundColor Yellow
        Remove-Item -Path "venv" -Recurse -Force
        python -m venv venv
        Write-Host "  ✓ Entorno virtual recreado" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Usando entorno virtual existente" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "  ✓ Entorno virtual creado" -ForegroundColor Green
}

# 3. Activar entorno virtual
Write-Host ""
Write-Host "[3/6] Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Entorno activado" -ForegroundColor Green

# 4. Actualizar pip
Write-Host ""
Write-Host "[4/6] Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ pip actualizado" -ForegroundColor Green

# 5. Instalar dependencias
Write-Host ""
Write-Host "[5/6] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "  Esto puede tomar varios minutos..." -ForegroundColor Cyan

$installChoice = Read-Host @"
  
  Seleccione versión de dependencias:
  [1] Actualizada (TensorFlow 2.15+ - Recomendado)
  [2] Legacy (TensorFlow 2.8 - Más compatible)
  
  Opción
"@

if ($installChoice -eq "2") {
    # Crear requirements_legacy.txt temporal
    Write-Host "  Instalando versión legacy..." -ForegroundColor Yellow
    
    $legacyContent = @"
tensorflow==2.8.0
keras==2.8.0
mediapipe==0.8.11
numpy==1.21.6
opencv-python==4.5.5.64
pandas==1.4.4
pygame==2.5.2
Flask==3.0.2
protobuf==3.19.1
tables==3.7.0
PyQt5==5.15.9
gTTS==2.5.1
PyYAML==6.0.2
"@
    
    $legacyContent | Out-File -FilePath "requirements_legacy_temp.txt" -Encoding UTF8
    pip install -r requirements_legacy_temp.txt
    Remove-Item "requirements_legacy_temp.txt"
    
} else {
    Write-Host "  Instalando versión actualizada..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "  ❌ Error al instalar dependencias" -ForegroundColor Red
    Write-Host "  Intenta instalar manualmente: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# 6. Verificar instalación
Write-Host ""
Write-Host "[6/6] Verificando instalación..." -ForegroundColor Yellow

$tests = @(
    @{Name="TensorFlow"; Command="import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"},
    @{Name="MediaPipe"; Command="import mediapipe; print('MediaPipe OK')"},
    @{Name="OpenCV"; Command="import cv2; print(f'OpenCV {cv2.__version__}')"},
    @{Name="PyYAML"; Command="import yaml; print('PyYAML OK')"},
    @{Name="Config Manager"; Command="from config_manager import config; print(f'{len(config.get_word_ids())} palabras')"}
)

$allPassed = $true

foreach ($test in $tests) {
    try {
        $result = python -c $test.Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $($test.Name): $result" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $($test.Name): Error" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host "  ❌ $($test.Name): Error" -ForegroundColor Red
        $allPassed = $false
    }
}

# Resumen final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "  ✓ SETUP COMPLETADO EXITOSAMENTE      " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Lee la documentación: MIGRATION_GUIDE.md" -ForegroundColor White
    Write-Host "  2. Prueba el modelo: python evaluate_model.py" -ForegroundColor White
    Write-Host "  3. Interfaz gráfica: python main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Para activar el entorno en el futuro:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "  ⚠️  SETUP COMPLETADO CON ERRORES     " -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Consulta MIGRATION_GUIDE.md sección 'Problemas Comunes'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Soluciones rápidas:" -ForegroundColor Yellow
    Write-Host "  • Error protobuf: pip install protobuf==3.20.3 --force-reinstall" -ForegroundColor White
    Write-Host "  • Error MediaPipe: Usar Python 3.10 en lugar de 3.12" -ForegroundColor White
    Write-Host ""
}

Write-Host "Presiona Enter para salir..." -ForegroundColor Cyan
Read-Host
