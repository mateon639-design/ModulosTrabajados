# -*- coding: utf-8 -*-
"""
Script para actualizar manualmente el módulo Importe Data
Ejecutar en el shell de Odoo para aplicar los cambios de base de datos
"""

def migrate(cr, version):
    """Migra la base de datos a la nueva versión con soporte de conflictos."""
    
    # 1. Crear la tabla de conflictos si no existe
    cr.execute("""
        CREATE TABLE IF NOT EXISTS contact_import_conflict (
            id SERIAL PRIMARY KEY,
            wizard_id INTEGER NOT NULL REFERENCES contact_import_wizard(id) ON DELETE CASCADE,
            row_number INTEGER NOT NULL,
            new_name VARCHAR,
            new_vat VARCHAR,
            new_email VARCHAR,
            new_phone VARCHAR,
            new_mobile VARCHAR,
            existing_partner_id INTEGER REFERENCES res_partner(id) ON DELETE SET NULL,
            conflict_type VARCHAR NOT NULL,
            action VARCHAR NOT NULL DEFAULT 'update',
            import_data TEXT,
            create_uid INTEGER REFERENCES res_users(id) ON DELETE SET NULL,
            create_date TIMESTAMP,
            write_uid INTEGER REFERENCES res_users(id) ON DELETE SET NULL,
            write_date TIMESTAMP
        )
    """)
    
    # 2. Agregar columna has_conflicts si no existe
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='contact_import_wizard' AND column_name='has_conflicts'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE contact_import_wizard 
            ADD COLUMN has_conflicts BOOLEAN DEFAULT FALSE
        """)
    
    # 3. Agregar columna conflict_count si no existe
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='contact_import_wizard' AND column_name='conflict_count'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE contact_import_wizard 
            ADD COLUMN conflict_count INTEGER DEFAULT 0
        """)
    
    # 4. Crear índices
    cr.execute("""
        CREATE INDEX IF NOT EXISTS idx_conflict_wizard 
        ON contact_import_conflict(wizard_id)
    """)
    
    cr.execute("""
        CREATE INDEX IF NOT EXISTS idx_conflict_partner 
        ON contact_import_conflict(existing_partner_id)
    """)
    
    print("✓ Migración completada exitosamente")
    print("✓ Tabla contact_import_conflict creada")
    print("✓ Columnas has_conflicts y conflict_count agregadas")
    print("✓ Índices creados")
