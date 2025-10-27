# -*- coding: utf-8 -*-
{
    'name': 'Contacts Extension',
    'version': '18.0.2.0.0',
    'category': 'Contacts',
    'summary': 'Extensión personalizada del módulo de Contactos con Trazabilidad de Importación',
    'description': """
        Contacts Extension Module
        =========================
        
        Este módulo extiende la funcionalidad del módulo de Contactos (contacts) 
        de Odoo 18, proporcionando trazabilidad completa de importaciones.
        
        Características:
        ----------------
        * Hereda el modelo res.partner
        * Trazabilidad completa de importaciones (origen, fecha, región, tipo)
        * Contador de importaciones por contacto
        * Historial en el Chatter con detalles de cada importación
        * Filtros y agrupaciones por información de importación
        * Extiende las vistas de contactos
        * Compatible con Odoo 18
        * Integración perfecta con wizard de importación de estudiantes
        
        Campos de Trazabilidad:
        ----------------------
        * Origen de Importación (nombre del archivo)
        * Fecha de Importación
        * Región de Importación
        * Tipo de Importación (Estudiante/Profesor)
        * Última Actualización por Importación
        * Número de Importaciones
        
        Autor: Sistema de Desarrollo
        Versión de Odoo: 18.0
    """,
    'author': 'Tu Compañía',
    'website': 'https://www.tucompania.com',
    'license': 'LGPL-3',
    
    # Dependencias
    'depends': [
        'base',
        'contacts',
    ],
    
    # Archivos de datos
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    
    # Archivos de demostración (opcional)
    'demo': [],
    
    # Configuración de instalación
    'installable': True,
    'application': False,
    'auto_install': False,
    
    # Imágenes
    'images': [],
    
    # Assets web (si se necesitan en el futuro)
    'assets': {},
}
