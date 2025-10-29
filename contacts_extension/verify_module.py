"""
Script de Verificación del Módulo contacts_extension
Verifica que todos los archivos necesarios estén presentes y sean válidos
"""

import os
import sys

def check_file_exists(path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(path):
        print(f"  ✓ {description}")
        return True
    else:
        print(f"  ✗ {description} - NO ENCONTRADO")
        return False

def main():
    print("=" * 60)
    print("VERIFICACIÓN DEL MÓDULO CONTACTS_EXTENSION")
    print("=" * 60)
    print()
    
    module_path = r"c:\ModulosOdoo18\contacts_extension"
    
    if not os.path.exists(module_path):
        print(f"ERROR: No se encuentra el directorio del módulo: {module_path}")
        return False
    
    print(f"Directorio del módulo: {module_path}")
    print()
    
    # Verificar archivos principales
    print("Archivos Principales:")
    all_ok = True
    all_ok &= check_file_exists(
        os.path.join(module_path, "__init__.py"),
        "__init__.py (inicializador del módulo)"
    )
    all_ok &= check_file_exists(
        os.path.join(module_path, "__manifest__.py"),
        "__manifest__.py (manifiesto del módulo)"
    )
    print()
    
    # Verificar directorio models
    print("Directorio Models:")
    models_path = os.path.join(module_path, "models")
    all_ok &= check_file_exists(
        os.path.join(models_path, "__init__.py"),
        "models/__init__.py"
    )
    all_ok &= check_file_exists(
        os.path.join(models_path, "res_partner.py"),
        "models/res_partner.py (modelo principal)"
    )
    
    # Verificar que NO exista res_partner_survey.py
    survey_file = os.path.join(models_path, "res_partner_survey.py")
    if os.path.exists(survey_file):
        print(f"  ⚠ models/res_partner_survey.py - DEBERÍA SER ELIMINADO")
        all_ok = False
    else:
        print(f"  ✓ models/res_partner_survey.py - Correctamente eliminado")
    print()
    
    # Verificar directorio security
    print("Directorio Security:")
    security_path = os.path.join(module_path, "security")
    all_ok &= check_file_exists(
        os.path.join(security_path, "ir.model.access.csv"),
        "security/ir.model.access.csv"
    )
    print()
    
    # Verificar directorio views
    print("Directorio Views:")
    views_path = os.path.join(module_path, "views")
    all_ok &= check_file_exists(
        os.path.join(views_path, "res_partner_views.xml"),
        "views/res_partner_views.xml"
    )
    print()
    
    # Verificar el contenido del __init__.py de models
    print("Verificación de Contenido:")
    init_file = os.path.join(models_path, "__init__.py")
    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'res_partner_survey' in content:
                print("  ✗ models/__init__.py contiene referencia a res_partner_survey")
                print("    DEBE SER ELIMINADA")
                all_ok = False
            else:
                print("  ✓ models/__init__.py no contiene referencias a res_partner_survey")
    except Exception as e:
        print(f"  ✗ Error al leer models/__init__.py: {e}")
        all_ok = False
    print()
    
    # Verificar versión en __manifest__.py
    manifest_file = os.path.join(module_path, "__manifest__.py")
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "'version': '18.0.3.0.1'" in content or '"version": "18.0.3.0.1"' in content:
                print("  ✓ Versión actualizada a 18.0.3.0.1")
            else:
                print("  ⚠ Versión no actualizada (debería ser 18.0.3.0.1)")
    except Exception as e:
        print(f"  ✗ Error al leer __manifest__.py: {e}")
        all_ok = False
    print()
    
    # Resumen
    print("=" * 60)
    if all_ok:
        print("✓ VERIFICACIÓN EXITOSA - El módulo está listo para actualizar")
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Ve a Odoo (localhost:8069)")
        print("2. Apps > Busca 'Contacts Extension'")
        print("3. Haz clic en 'Actualizar' (Upgrade)")
    else:
        print("✗ VERIFICACIÓN FALLIDA - Revisa los errores arriba")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para salir...")
    sys.exit(0 if success else 1)
