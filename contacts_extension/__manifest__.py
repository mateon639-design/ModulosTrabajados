# -*- coding: utf-8 -*-
{
    'name': 'Contacts Extension',
    'version': '18.0.3.1.0',
    'category': 'Contacts',
    'summary': 'Extensión de Contactos con Trazabilidad e Historial de Encuestas',
    'description': """
        Contacts Extension Module
        =========================
        
        Este módulo extiende la funcionalidad del módulo de Contactos (contacts) 
        de Odoo 18, proporcionando trazabilidad completa de importaciones y 
        historial de participación en encuestas.
        
        Características:
        ----------------
        * Hereda el modelo res.partner
        * Trazabilidad completa de importaciones (origen, fecha, región, tipo)
        * Contador de importaciones por contacto
        * Historial en el Chatter con detalles de cada importación
        * Filtros y agrupaciones por información de importación
        * **NUEVO: Historial de Encuestas por contacto**
        * **NUEVO: Estadísticas de participación en encuestas**
        * **NUEVO: Visualización de puntajes y resultados**
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
        
        Historial de Encuestas:
        ----------------------
        * Pestaña dedicada "Historial de Encuestas"
        * Lista completa de participaciones
        * Estados: Sin iniciar, En progreso, Completada
        * Fecha de inicio y finalización
        * Puntajes obtenidos (para encuestas calificables)
        * Resultado: Aprobado/Reprobado
        * Estadísticas: Total, Completadas, En proceso
        * Promedio de puntajes
        * Última fecha de participación
        * Botones inteligentes para acceso rápido
        
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
    
    # Dependencias externas (opcionales)
    # Si 'survey' está instalado, se habilitará el historial de encuestas
    'external_dependencies': {
        'python': [],
    },
    
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
