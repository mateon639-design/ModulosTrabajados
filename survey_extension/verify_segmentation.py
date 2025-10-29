# -*- coding: utf-8 -*-
"""
Script de verificación para la funcionalidad de Segmentación
Versión 1.5.0 - Survey Extension

Este script verifica que todos los componentes de segmentación
estén correctamente instalados y funcionando.
"""

import sys
import os

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    print("=" * 70)
    print("VERIFICACIÓN DE ARCHIVOS DE SEGMENTACIÓN")
    print("=" * 70)
    
    archivos_requeridos = [
        # Modelos
        "models/survey_region.py",
        "models/survey_user_input_extensions.py",
        "models/survey_survey_inherit.py",
        
        # Vistas
        "views/survey_region_views.xml",
        "views/survey_user_input_segmentation_views.xml",
        "views/survey_survey_inherit_views.xml",
        
        # Data
        "data/survey_regions.xml",
        
        # Seguridad
        "security/ir.model.access.csv",
        
        # Menús
        "views/survey_extension_menu.xml",
    ]
    
    base_path = os.path.dirname(__file__)
    todos_existen = True
    
    for archivo in archivos_requeridos:
        ruta_completa = os.path.join(base_path, archivo)
        existe = os.path.exists(ruta_completa)
        estado = "✓ OK" if existe else "✗ FALTA"
        print(f"{estado:8} {archivo}")
        
        if not existe:
            todos_existen = False
    
    print("\n" + "=" * 70)
    if todos_existen:
        print("✓ TODOS LOS ARCHIVOS ESTÁN PRESENTES")
    else:
        print("✗ FALTAN ARCHIVOS - Revisa los marcados con ✗")
    print("=" * 70)
    
    return todos_existen


def verificar_manifest():
    """Verifica que el manifest tenga los archivos registrados"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DEL MANIFEST")
    print("=" * 70)
    
    manifest_path = os.path.join(os.path.dirname(__file__), "__manifest__.py")
    
    archivos_data = [
        "data/survey_regions.xml",
    ]
    
    archivos_views = [
        "views/survey_region_views.xml",
        "views/survey_user_input_segmentation_views.xml",
    ]
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        todos_registrados = True
        
        print("\nArchivos de DATA:")
        for archivo in archivos_data:
            registrado = archivo in contenido
            estado = "✓ Registrado" if registrado else "✗ NO registrado"
            print(f"  {estado:15} {archivo}")
            if not registrado:
                todos_registrados = False
        
        print("\nArchivos de VISTAS:")
        for archivo in archivos_views:
            registrado = archivo in contenido
            estado = "✓ Registrado" if registrado else "✗ NO registrado"
            print(f"  {estado:15} {archivo}")
            if not registrado:
                todos_registrados = False
        
        # Verificar versión
        if '"version": "1.5.0"' in contenido:
            print("\n✓ Versión actualizada a 1.5.0")
        else:
            print("\n⚠ La versión debería ser 1.5.0")
            todos_registrados = False
        
        print("\n" + "=" * 70)
        if todos_registrados:
            print("✓ MANIFEST CORRECTAMENTE CONFIGURADO")
        else:
            print("✗ REVISAR MANIFEST - Algunos archivos no están registrados")
        print("=" * 70)
        
        return todos_registrados
        
    except Exception as e:
        print(f"✗ Error al leer manifest: {e}")
        return False


def verificar_modelos():
    """Verifica imports en __init__.py de models"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE IMPORTS DE MODELOS")
    print("=" * 70)
    
    init_path = os.path.join(os.path.dirname(__file__), "models", "__init__.py")
    
    try:
        with open(init_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        imports_requeridos = [
            "survey_region",
            "survey_user_input_extensions",
            "survey_survey_inherit",
        ]
        
        todos_importados = True
        
        for import_name in imports_requeridos:
            importado = f"from . import {import_name}" in contenido
            estado = "✓ Importado" if importado else "✗ NO importado"
            print(f"  {estado:15} {import_name}")
            if not importado:
                todos_importados = False
        
        print("\n" + "=" * 70)
        if todos_importados:
            print("✓ TODOS LOS MODELOS ESTÁN IMPORTADOS")
        else:
            print("✗ FALTAN IMPORTS EN models/__init__.py")
        print("=" * 70)
        
        return todos_importados
        
    except Exception as e:
        print(f"✗ Error al leer models/__init__.py: {e}")
        return False


def verificar_seguridad():
    """Verifica entradas en ir.model.access.csv"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE SEGURIDAD")
    print("=" * 70)
    
    csv_path = os.path.join(os.path.dirname(__file__), "security", "ir.model.access.csv")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        permisos_requeridos = [
            "access_survey_region_user",
            "access_survey_region_public",
        ]
        
        todos_definidos = True
        
        for permiso in permisos_requeridos:
            definido = permiso in contenido
            estado = "✓ Definido" if definido else "✗ NO definido"
            print(f"  {estado:15} {permiso}")
            if not definido:
                todos_definidos = False
        
        print("\n" + "=" * 70)
        if todos_definidos:
            print("✓ PERMISOS CORRECTAMENTE CONFIGURADOS")
        else:
            print("✗ FALTAN PERMISOS EN ir.model.access.csv")
        print("=" * 70)
        
        return todos_definidos
        
    except Exception as e:
        print(f"✗ Error al leer ir.model.access.csv: {e}")
        return False


def main():
    """Función principal"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  VERIFICACIÓN DE INSTALACIÓN - MÓDULO SURVEY EXTENSION v1.5.0".center(68) + "║")
    print("║" + "  Funcionalidad: Segmentación por Región y Tipo".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(("Archivos", verificar_archivos()))
    resultados.append(("Manifest", verificar_manifest()))
    resultados.append(("Modelos", verificar_modelos()))
    resultados.append(("Seguridad", verificar_seguridad()))
    
    # Resumen final
    print("\n\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  RESUMEN DE VERIFICACIÓN".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╠" + "═" * 68 + "╣")
    
    todos_ok = True
    for nombre, resultado in resultados:
        estado = "✓ PASS" if resultado else "✗ FAIL"
        linea = f"║  {nombre:20} {estado:44}  ║"
        print(linea)
        if not resultado:
            todos_ok = False
    
    print("╠" + "═" * 68 + "╣")
    
    if todos_ok:
        print("║" + " " * 68 + "║")
        print("║" + "  ✓ TODAS LAS VERIFICACIONES PASARON CORRECTAMENTE".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("║" + "  El módulo está listo para actualizar en Odoo.".center(68) + "║")
        print("║" + "  Ejecuta: Apps > Survey Extension > Actualizar".center(68) + "║")
        print("║" + " " * 68 + "║")
    else:
        print("║" + " " * 68 + "║")
        print("║" + "  ✗ ALGUNAS VERIFICACIONES FALLARON".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("║" + "  Revisa los detalles arriba y corrige los errores.".center(68) + "║")
        print("║" + " " * 68 + "║")
    
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    return 0 if todos_ok else 1


if __name__ == "__main__":
    sys.exit(main())
