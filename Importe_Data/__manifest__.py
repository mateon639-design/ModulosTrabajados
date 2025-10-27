# -*- coding: utf-8 -*-
{
    'name': 'Importe Data',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Importación masiva de contactos con historial completo',
    'description': """
        Importe Data - Sistema de Importación Masiva
        ============================================
        
        Este módulo permite importar contactos de forma masiva desde diferentes formatos de archivo
        con un completo sistema de historial y trazabilidad.
        
        Características principales:
        * Historial completo con vistas Kanban, Lista y Formulario
        * Importación desde archivos CSV, Excel (XLSX) y XML
        * Mapeo flexible de campos
        * Vista previa antes de importar
        * Detección automática de duplicados
        * Actualización de registros existentes
        * Log de errores detallado
        * Estadísticas visuales con gráficos de progreso
        * Filtros avanzados por estado, tipo, fecha y usuario
        * Acceso directo a contactos creados/actualizados
        * Soporte para estudiantes y profesores
        * Trazabilidad completa de importaciones
        
        Formatos soportados:
        -------------------
        - CSV con delimitadores configurables
        - Excel (XLSX) con openpyxl
        - XML con estructura personalizable
        
        Proceso de importación:
        ----------------------
        1. Cargar archivo
        2. Mapear campos a Odoo
        3. Previsualizar datos
        4. Confirmar e importar
        5. Revisar resultados
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
    ],
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/import_history_views.xml',
        'views/contact_import_wizard_views.xml',
        'views/menu_views.xml',
        'data/ejemplo_contactos.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 100,
}
