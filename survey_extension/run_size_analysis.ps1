# Script para ejecutar el análisis de tamaño de encuestas en Odoo
# Asegúrate de cambiar el nombre de la base de datos si es diferente

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "ANÁLISIS DE ESPACIO EN DISCO - ENCUESTAS ODOO" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio de Odoo
$odooPath = "C:\Program Files\Odoo 18.0.20251001"
Set-Location $odooPath

Write-Host "📂 Ubicación de Odoo: $odooPath" -ForegroundColor Green
Write-Host ""

# Solicitar nombre de base de datos
Write-Host "Ingrese el nombre de su base de datos Odoo:" -ForegroundColor Yellow
$dbName = Read-Host "Nombre de DB"

if ([string]::IsNullOrWhiteSpace($dbName)) {
    Write-Host "❌ Error: Debe proporcionar un nombre de base de datos" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 Conectando a base de datos: $dbName" -ForegroundColor Cyan
Write-Host "⏳ Ejecutando análisis..." -ForegroundColor Cyan
Write-Host ""

# Crear comando para ejecutar en shell de Odoo
$scriptPath = "c:\ModulosOdoo18\survey_extension\calculate_survey_size.py"
$pythonCode = @"
exec(open(r'$scriptPath').read())
calculate_survey_storage_size(env)
"@

# Ejecutar odoo shell con el script
$process = Start-Process -FilePath "python" `
    -ArgumentList "odoo-bin", "shell", "-d", $dbName, "-c", "server\conf\odoo.conf", "--no-http" `
    -NoNewWindow -PassThru -Wait `
    -RedirectStandardInput "temp_input.txt"

# Crear archivo temporal con comandos
$pythonCode | Out-File -FilePath "temp_input.txt" -Encoding UTF8

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ Análisis completado" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

# Limpiar archivo temporal
if (Test-Path "temp_input.txt") {
    Remove-Item "temp_input.txt"
}
