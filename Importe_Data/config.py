# -*- coding: utf-8 -*-
"""
Configuración global para el módulo Importe Data.
"""

# Configuración de tipos de contacto
CONTACT_TYPES = [
    ('student', 'Estudiante'),
    ('teacher', 'Profesor'),
]

# Mapeo automático de nombres de columnas a campos de Odoo
FIELD_MAPPINGS = {
    # Nombre
    'nombre': 'name',
    'name': 'name',
    'apellido': 'name',
    'full_name': 'name',
    'nombre_completo': 'name',
    
    # Documento/Identificación
    'documento': 'vat',
    'vat': 'vat',
    'dni': 'vat',
    'identificacion': 'vat',
    'cedula': 'vat',
    'nif': 'vat',
    'cif': 'vat',
    
    # Email
    'email': 'email',
    'correo': 'email',
    'mail': 'email',
    'correo_electronico': 'email',
    'e-mail': 'email',
    
    # Teléfono
    'telefono': 'phone',
    'phone': 'phone',
    'tel': 'phone',
    'fijo': 'phone',
    'landline': 'phone',
    
    # Móvil
    'celular': 'mobile',
    'mobile': 'mobile',
    'movil': 'mobile',
    'cell': 'mobile',
    'cellular': 'mobile',
    
    # Dirección
    'direccion': 'street',
    'street': 'street',
    'calle': 'street',
    'address': 'street',
    'domicilio': 'street',
    
    # Ciudad
    'ciudad': 'city',
    'city': 'city',
    'poblacion': 'city',
    'localidad': 'city',
    
    # País
    'pais': 'country_id',
    'country': 'country_id',
    'country_id': 'country_id',
    
    # Comentarios/Notas
    'grado': 'comment',
    'curso': 'comment',
    'nivel': 'comment',
    'comentario': 'comment',
    'comment': 'comment',
    'notas': 'comment',
    'notes': 'comment',
    'observaciones': 'comment',
}

# Delimitadores CSV soportados
CSV_DELIMITERS = [
    (',', 'Coma (,)'),
    (';', 'Punto y coma (;)'),
    ('\t', 'Tabulador'),
    ('|', 'Tubería (|)'),
]

# Codificaciones soportadas
CSV_ENCODINGS = [
    ('utf-8', 'UTF-8'),
    ('latin-1', 'Latin-1'),
    ('cp1252', 'Windows-1252'),
    ('iso-8859-1', 'ISO-8859-1'),
]

# Configuración de vista previa
PREVIEW_MAX_ROWS = 10

# Extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {
    'csv': ['csv', 'txt'],
    'xlsx': ['xlsx', 'xls'],
    'xml': ['xml'],
}

# Mensajes de error comunes
ERROR_MESSAGES = {
    'no_file': 'Debe cargar un archivo válido (CSV, XLSX o XML).',
    'no_columns': 'No se pudieron detectar columnas en el archivo.',
    'no_mapping': 'Debe mapear al menos un campo antes de continuar.',
    'no_data': 'No hay datos para importar.',
    'no_name_email': 'Debe tener al menos Nombre o Email.',
    'openpyxl_missing': 'La librería openpyxl no está instalada. Instálela con: pip install openpyxl',
    'encoding_error': 'Error de codificación. Intente con otra codificación (UTF-8, Latin-1, Windows-1252).',
    'csv_error': 'Error al leer el archivo CSV',
    'xlsx_error': 'Error al leer el archivo Excel',
    'xml_error': 'Error al leer el archivo XML',
    'xml_no_records': 'No se encontraron registros en el archivo XML.',
    'xml_invalid': 'El archivo XML no tiene un formato válido.',
}

# Configuración de trazabilidad
TRACKING_FIELDS = [
    'import_source',
    'import_date',
    'import_region',
    'import_type',
    'last_import_update',
]
