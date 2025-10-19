# Script de Inicio - LSP Web Application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   LSP Web Application - Inicio" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detener proceso en puerto 5000
$portProc = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($portProc) {
    Write-Host "Deteniendo proceso en puerto 5000..." -ForegroundColor Yellow
    Stop-Process -Id $portProc.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "Iniciando servidor..." -ForegroundColor Green
Write-Host "URL: http://localhost:5000/" -ForegroundColor Cyan
Write-Host "Demo: http://localhost:5000/demo" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "web-app\backend"

# Detectar Python
if (Test-Path "..\..\..\.venv\Scripts\python.exe") {
    & "..\..\..\.venv\Scripts\python.exe" app.py
} else {
    py -3.10 app.py
}
