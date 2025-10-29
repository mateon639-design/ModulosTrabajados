# -*- coding: utf-8 -*-
"""
Script para actualizar el módulo contacts_extension de forma segura.
Ejecutar desde el directorio del módulo.
"""

import sys
import os

# Agregar la ruta de Odoo al PYTHONPATH
odoo_path = r"C:\Program Files\Odoo 18.0.20251001\server"
if odoo_path not in sys.path:
    sys.path.insert(0, odoo_path)

print("=" * 70)
print("ACTUALIZACIÓN DEL MÓDULO: contacts_extension")
print("=" * 70)
print()

# Verificar que el módulo existe
module_path = r"c:\ModulosOdoo18\contacts_extension"
if not os.path.exists(module_path):
    print(f"❌ ERROR: No se encuentra el módulo en {module_path}")
    sys.exit(1)

print(f"✓ Módulo encontrado en: {module_path}")
print()

# Verificar archivos críticos
critical_files = [
    "__manifest__.py",
    "__init__.py",
    "models/__init__.py",
    "models/res_partner.py",
    "views/res_partner_views.xml",
    "security/ir.model.access.csv",
]

print("Verificando archivos críticos:")
all_ok = True
for file in critical_files:
    file_path = os.path.join(module_path, file)
    exists = os.path.exists(file_path)
    status = "✓" if exists else "❌"
    print(f"  {status} {file}")
    if not exists:
        all_ok = False

print()

if not all_ok:
    print("❌ ERROR: Faltan archivos críticos")
    sys.exit(1)

print("=" * 70)
print("IMPORTANTE: Pasos para actualizar el módulo")
print("=" * 70)
print()
print("1. Abre Odoo en tu navegador: http://localhost:8069")
print("2. Ve a: Aplicaciones > Aplicaciones")
print("3. Quita el filtro 'Aplicaciones' de la búsqueda")
print("4. Busca: 'Contacts Extension'")
print()
print("OPCIÓN A - Si el módulo está instalado:")
print("  - Haz clic en 'Actualizar'")
print()
print("OPCIÓN B - Si el módulo no está instalado:")
print("  - Haz clic en 'Instalar'")
print()
print("OPCIÓN C - Actualizar desde terminal:")
print("  cd \"C:\\Program Files\\Odoo 18.0.20251001\\python\"")
print("  .\\python.exe ..\\server\\odoo-bin -c ..\\server\\odoo.conf -d odoo18 -u contacts_extension --stop-after-init")
print()
print("=" * 70)
print()

input("Presiona Enter para salir...")
