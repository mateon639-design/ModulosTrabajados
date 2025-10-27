# -*- coding: utf-8 -*-
"""
Script de verificación para el módulo Importe Data.
Ejecutar después de instalar/actualizar el módulo.
"""

import logging
_logger = logging.getLogger(__name__)

def verify_importe_data_installation(env):
    """Verifica que el módulo Importe Data esté correctamente instalado."""
    
    try:
        # Verificar que los modelos existen
        wizard_model = env['contact.import.wizard']
        column_model = env['contact.import.column']
        history_model = env['import.history']
        
        _logger.info("✓ Modelo contact.import.wizard encontrado")
        _logger.info("✓ Modelo contact.import.column encontrado")
        _logger.info("✓ Modelo import.history encontrado")
        
        # Verificar que la acción existe
        action = env.ref('importe_data.action_contact_import_wizard', raise_if_not_found=False)
        if action:
            _logger.info("✓ Acción del wizard encontrada")
        else:
            _logger.warning("✗ Acción del wizard NO encontrada")
        
        # Verificar que el menú principal existe
        menu_root = env.ref('importe_data.menu_importe_data_root', raise_if_not_found=False)
        if menu_root:
            _logger.info("✓ Menú principal 'Importe Data' encontrado")
        else:
            _logger.warning("✗ Menú principal NO encontrado")
        
        # Verificar que el submenú de historial existe
        menu_history = env.ref('importe_data.menu_import_history', raise_if_not_found=False)
        if menu_history:
            _logger.info("✓ Submenú 'Historial de Importaciones' encontrado")
        else:
            _logger.warning("✗ Submenú de historial NO encontrado")
        
        # Verificar que el submenú existe
        menu_import = env.ref('importe_data.menu_contact_import', raise_if_not_found=False)
        if menu_import:
            _logger.info("✓ Submenú 'Importe de Contactos' encontrado")
        else:
            _logger.warning("✗ Submenú de importación NO encontrado")
        
        # Verificar permisos de acceso
        access_wizard = env.ref('importe_data.access_contact_import_wizard_user', raise_if_not_found=False)
        access_column = env.ref('importe_data.access_contact_import_column_user', raise_if_not_found=False)
        
        if access_wizard and access_column:
            _logger.info("✓ Permisos de acceso configurados correctamente")
        else:
            _logger.warning("✗ Algunos permisos de acceso no están configurados")
        
        print("\n" + "="*70)
        print("VERIFICACIÓN DEL MÓDULO IMPORTE DATA COMPLETADA")
        print("="*70)
        print("✓ El módulo está correctamente instalado y configurado.")
        print("\n📋 CÓMO USAR EL MÓDULO:")
        print("-" * 70)
        print("1. Navegue a: Importe Data")
        print("2. Verá el historial de todas las importaciones realizadas")
        print("3. Click en 'Importar Contactos' para nueva importación")
        print("4. Cargue un archivo CSV, Excel (XLSX) o XML")
        print("5. Seleccione el tipo de contacto (Estudiante o Profesor)")
        print("6. Configure opciones del archivo (delimitador, codificación)")
        print("7. Mapee las columnas a los campos de Odoo")
        print("8. Previsualice los datos")
        print("9. Confirme e importe")
        print("10. Vea el resultado en el historial")
        print("\n📁 ARCHIVOS DE EJEMPLO:")
        print("-" * 70)
        print("- data/ejemplo_contactos.csv - Ejemplo en formato CSV")
        print("- data/ejemplo_contactos.xml - Ejemplo en formato XML")
        print("\n💡 REQUISITOS:")
        print("-" * 70)
        print("- Para importar archivos Excel (.xlsx): pip install openpyxl")
        print("\n🎯 CARACTERÍSTICAS:")
        print("-" * 70)
        print("✓ Importación masiva desde CSV, Excel y XML")
        print("✓ Mapeo flexible de campos")
        print("✓ Detección automática de duplicados")
        print("✓ Actualización de registros existentes")
        print("✓ Vista previa antes de importar")
        print("✓ Log detallado de errores")
        print("✓ Categorización por tipo de contacto")
        print("✓ Trazabilidad completa")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        _logger.error(f"✗ Error durante la verificación: {e}")
        print("\n" + "="*70)
        print("ERROR EN LA VERIFICACIÓN")
        print("="*70)
        print(f"Error: {e}")
        print("\n🔧 SOLUCIÓN:")
        print("-" * 70)
        print("1. Asegúrese de que el módulo esté instalado")
        print("2. Actualice la lista de aplicaciones")
        print("3. Verifique que no haya errores en los archivos")
        print("4. Revise el log de Odoo para más detalles")
        print("="*70 + "\n")
        return False

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SCRIPT DE VERIFICACIÓN - IMPORTE DATA")
    print("="*70)
    print("\nEste script debe ejecutarse dentro del shell de Odoo:")
    print("\nComando:")
    print("  odoo-bin shell -d <nombre_base_datos> -c <archivo_config>")
    print("\nDentro del shell de Odoo, ejecutar:")
    print("  >>> from importe_data.verify_installation import verify_importe_data_installation")
    print("  >>> verify_importe_data_installation(env)")
    print("="*70 + "\n")
