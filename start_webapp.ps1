# ===================================================# ===================================================

# Script de Inicio Rapido - LSP Web Application# Script de Inicio Rápido - LSP Web Application

# ===================================================# ===================================================



# Cambiar al directorio del scriptWrite-Host "========================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.PathWrite-Host "   LSP Web Application - Inicio" -ForegroundColor Cyan

Set-Location -Path $ScriptDirWrite-Host "========================================" -ForegroundColor Cyan

Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan

Write-Host "   LSP Web Application - Inicio" -ForegroundColor Cyan# Verificar Python 3.10

Write-Host "========================================" -ForegroundColor CyanWrite-Host "[1/4] Verificando Python 3.10..." -ForegroundColor Yellow

Write-Host ""$pythonVersion = py -3.10 --version 2>&1

Write-Host "Directorio de trabajo: $ScriptDir" -ForegroundColor Grayif ($LASTEXITCODE -eq 0) {

Write-Host ""    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green

} else {

# Verificar Python 3.10    Write-Host "✗ Error: Python 3.10 no encontrado" -ForegroundColor Red

Write-Host "[1/5] Verificando Python 3.10..." -ForegroundColor Yellow    Write-Host "  Instala Python 3.10 desde: https://www.python.org/" -ForegroundColor Yellow

$pythonVersion = py -3.10 --version 2>&1    exit 1

if ($LASTEXITCODE -eq 0) {}

    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green

} else {# Verificar dependencias web

    Write-Host "Error: Python 3.10 no encontrado" -ForegroundColor RedWrite-Host ""

    Write-Host "  Instala Python 3.10 desde: https://www.python.org/" -ForegroundColor YellowWrite-Host "[2/4] Verificando dependencias web..." -ForegroundColor Yellow

    exit 1$flaskInstalled = py -3.10 -c "import flask; print(flask.__version__)" 2>&1

}if ($LASTEXITCODE -eq 0) {

    Write-Host "✓ Flask instalado: v$flaskInstalled" -ForegroundColor Green

# Detectar entorno virtual} else {

Write-Host ""    Write-Host "! Flask no encontrado. Instalando..." -ForegroundColor Yellow

Write-Host "[2/5] Detectando entorno virtual..." -ForegroundColor Yellow    py -3.10 -m pip install -r web-app\requirements_webapp.txt --user

$venvPython = $null}

if (Test-Path "..\..\.venv\Scripts\python.exe") {

    $venvPython = Resolve-Path "..\..\.venv\Scripts\python.exe"$socketioInstalled = py -3.10 -c "import flask_socketio; print('OK')" 2>&1

    Write-Host "Encontrado: .venv (2 niveles arriba)" -ForegroundColor Greenif ($LASTEXITCODE -eq 0) {

} elseif (Test-Path "..\.venv\Scripts\python.exe") {    Write-Host "✓ Flask-SocketIO instalado" -ForegroundColor Green

    $venvPython = Resolve-Path "..\.venv\Scripts\python.exe"} else {

    Write-Host "Encontrado: .venv (1 nivel arriba)" -ForegroundColor Green    Write-Host "! Flask-SocketIO no encontrado. Instalando..." -ForegroundColor Yellow

} elseif (Test-Path "venv\Scripts\python.exe") {    py -3.10 -m pip install flask-socketio python-socketio --user

    $venvPython = Resolve-Path "venv\Scripts\python.exe"}

    Write-Host "Encontrado: venv (local)" -ForegroundColor Green

} else {# Verificar modelo

    Write-Host "No se encontro entorno virtual, usando Python global" -ForegroundColor YellowWrite-Host ""

    $venvPython = "py -3.10"Write-Host "[3/4] Verificando modelo LSP..." -ForegroundColor Yellow

}if (Test-Path "models\actions_15.keras") {

    Write-Host "✓ Modelo encontrado: models\actions_15.keras" -ForegroundColor Green

# Verificar dependencias web} else {

Write-Host ""    Write-Host "✗ Error: Modelo no encontrado en models\actions_15.keras" -ForegroundColor Red

Write-Host "[3/5] Verificando dependencias web..." -ForegroundColor Yellow    exit 1

$flaskCheck = if ($venvPython -eq "py -3.10") { }

    py -3.10 -c "import flask; print(flask.__version__)" 2>&1 

} else { if (Test-Path "models\words.json") {

    & $venvPython -c "import flask; print(flask.__version__)" 2>&1     Write-Host "✓ Vocabulario encontrado: models\words.json" -ForegroundColor Green

}} else {

    Write-Host "✗ Error: Vocabulario no encontrado en models\words.json" -ForegroundColor Red

if ($LASTEXITCODE -eq 0) {    exit 1

    Write-Host "Flask instalado correctamente" -ForegroundColor Green}

} else {

    Write-Host "Flask no encontrado. Instalando..." -ForegroundColor Yellow# Iniciar servidor

    if ($venvPython -eq "py -3.10") {Write-Host ""

        py -3.10 -m pip install -r web-app\requirements_webapp.txtWrite-Host "[4/4] Iniciando servidor web..." -ForegroundColor Yellow

    } else {Write-Host ""

        & $venvPython -m pip install -r web-app\requirements_webapp.txtWrite-Host "========================================" -ForegroundColor Cyan

    }Write-Host "   Servidor LSP Web Application" -ForegroundColor Cyan

}Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""

# Verificar modeloWrite-Host "📍 Página Principal: http://localhost:5000/" -ForegroundColor Green

Write-Host ""Write-Host "🎥 Demo Interactivo: http://localhost:5000/demo" -ForegroundColor Green

Write-Host "[4/5] Verificando modelo LSP..." -ForegroundColor YellowWrite-Host "🔧 API Health: http://localhost:5000/api/health" -ForegroundColor Green

if (Test-Path "models\actions_15.keras") {Write-Host ""

    Write-Host "Modelo encontrado: models\actions_15.keras" -ForegroundColor GreenWrite-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow

} else {Write-Host ""

    Write-Host "Error: Modelo no encontrado en models\actions_15.keras" -ForegroundColor Red

    exit 1# Cambiar al directorio backend y ejecutar

}Set-Location -Path "web-app\backend"

py -3.10 app.py

if (Test-Path "models\words.json") {
    Write-Host "Vocabulario encontrado: models\words.json" -ForegroundColor Green
} else {
    Write-Host "Error: Vocabulario no encontrado en models\words.json" -ForegroundColor Red
    exit 1
}

# Detener procesos en puerto 5000
Write-Host ""
Write-Host "[5/5] Verificando puerto 5000..." -ForegroundColor Yellow
$portProcess = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($portProcess) {
    $pid = $portProcess.OwningProcess
    Write-Host "Puerto 5000 en uso por proceso PID: $pid" -ForegroundColor Yellow
    Write-Host "Deteniendo proceso..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Proceso detenido" -ForegroundColor Green
} else {
    Write-Host "Puerto 5000 disponible" -ForegroundColor Green
}

# Iniciar servidor
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Servidor LSP Web Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pagina Principal: http://localhost:5000/" -ForegroundColor Green
Write-Host "Demo Interactivo: http://localhost:5000/demo" -ForegroundColor Green
Write-Host "API Health: http://localhost:5000/api/health" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Cambiar al directorio backend y ejecutar
Set-Location -Path "web-app\backend"

if ($venvPython -eq "py -3.10") {
    py -3.10 app.py
} else {
    & $venvPython app.py
}
