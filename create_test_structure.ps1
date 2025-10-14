# Script para crear estructura de tests
# Ejecutar: .\create_test_structure.ps1

Write-Host "Creando estructura de tests..." -ForegroundColor Green

# Crear directorios
$dirs = @(
    "tests",
    "tests\unit",
    "tests\integration",
    "tests\fixtures",
    "tests\fixtures\sample_frames"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
        Write-Host "✓ Creado: $dir" -ForegroundColor Cyan
    } else {
        Write-Host "○ Ya existe: $dir" -ForegroundColor Yellow
    }
}

# Crear archivos __init__.py
$initFiles = @(
    "tests\__init__.py",
    "tests\unit\__init__.py",
    "tests\integration\__init__.py"
)

foreach ($file in $initFiles) {
    if (!(Test-Path $file)) {
        '"""Test suite para proyecto LSP"""' | Out-File -FilePath $file -Encoding UTF8
        Write-Host "✓ Creado: $file" -ForegroundColor Cyan
    }
}

Write-Host "`n✅ Estructura de tests creada exitosamente!" -ForegroundColor Green
Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
Write-Host "1. pytest tests/unit -v" -ForegroundColor White
Write-Host "2. pytest --cov=. --cov-report=html" -ForegroundColor White
Write-Host "3. git init" -ForegroundColor White
