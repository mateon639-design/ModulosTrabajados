# Script para actualizar el módulo contacts_extension
# Ejecutar este script para actualizar el módulo después de hacer cambios

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Actualizando módulo contacts_extension" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Ir al directorio del módulo
$modulePath = "c:\ModulosOdoo18\contacts_extension"
Set-Location $modulePath

Write-Host "Módulo: contacts_extension" -ForegroundColor Green
Write-Host "Ruta: $modulePath" -ForegroundColor Yellow
Write-Host ""

Write-Host "Cambios aplicados:" -ForegroundColor Green
Write-Host "  ✓ Eliminada dependencia de One2many con survey.user_input" -ForegroundColor White
Write-Host "  ✓ Convertido survey_input_ids a Many2many computado" -ForegroundColor White
Write-Host "  ✓ Agregado método _compute_survey_inputs" -ForegroundColor White
Write-Host "  ✓ Actualizado _compute_survey_statistics para buscar encuestas" -ForegroundColor White
Write-Host "  ✓ Eliminado archivo res_partner_survey.py innecesario" -ForegroundColor White
Write-Host "  ✓ Versión actualizada a 18.0.3.0.1" -ForegroundColor White
Write-Host ""

Write-Host "PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "1. Ve a Odoo en tu navegador (localhost:8069)" -ForegroundColor White
Write-Host "2. Ve a Apps (Aplicaciones)" -ForegroundColor White
Write-Host "3. Busca 'Contacts Extension'" -ForegroundColor White
Write-Host "4. Haz clic en el botón 'Actualizar' (Upgrade)" -ForegroundColor White
Write-Host ""

Write-Host "NOTA IMPORTANTE:" -ForegroundColor Magenta
Write-Host "Si el error persiste, es posible que necesites:" -ForegroundColor White
Write-Host "  - Reiniciar el servidor de Odoo" -ForegroundColor White
Write-Host "  - Desinstalar y reinstalar el módulo" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para continuar..."
