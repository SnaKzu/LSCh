# ===================================================
# Script de Inicio Rápido - LSP Web Application
# ===================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   LSP Web Application - Inicio" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python 3.10
Write-Host "[1/4] Verificando Python 3.10..." -ForegroundColor Yellow
$pythonVersion = py -3.10 --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Error: Python 3.10 no encontrado" -ForegroundColor Red
    Write-Host "  Instala Python 3.10 desde: https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Verificar dependencias web
Write-Host ""
Write-Host "[2/4] Verificando dependencias web..." -ForegroundColor Yellow
$flaskInstalled = py -3.10 -c "import flask; print(flask.__version__)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Flask instalado: v$flaskInstalled" -ForegroundColor Green
} else {
    Write-Host "! Flask no encontrado. Instalando..." -ForegroundColor Yellow
    py -3.10 -m pip install -r web-app\requirements_webapp.txt --user
}

$socketioInstalled = py -3.10 -c "import flask_socketio; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Flask-SocketIO instalado" -ForegroundColor Green
} else {
    Write-Host "! Flask-SocketIO no encontrado. Instalando..." -ForegroundColor Yellow
    py -3.10 -m pip install flask-socketio python-socketio --user
}

# Verificar modelo
Write-Host ""
Write-Host "[3/4] Verificando modelo LSP..." -ForegroundColor Yellow
if (Test-Path "models\actions_15.keras") {
    Write-Host "✓ Modelo encontrado: models\actions_15.keras" -ForegroundColor Green
} else {
    Write-Host "✗ Error: Modelo no encontrado en models\actions_15.keras" -ForegroundColor Red
    exit 1
}

if (Test-Path "models\words.json") {
    Write-Host "✓ Vocabulario encontrado: models\words.json" -ForegroundColor Green
} else {
    Write-Host "✗ Error: Vocabulario no encontrado en models\words.json" -ForegroundColor Red
    exit 1
}

# Iniciar servidor
Write-Host ""
Write-Host "[4/4] Iniciando servidor web..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Servidor LSP Web Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Página Principal: http://localhost:5000/" -ForegroundColor Green
Write-Host "🎥 Demo Interactivo: http://localhost:5000/demo" -ForegroundColor Green
Write-Host "🔧 API Health: http://localhost:5000/api/health" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Cambiar al directorio backend y ejecutar
Set-Location -Path "web-app\backend"
py -3.10 app.py
