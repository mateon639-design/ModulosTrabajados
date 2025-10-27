-- Script de migración para agregar nuevas columnas y tabla de conflictos
-- Ejecutar en el shell de Odoo o directamente en PostgreSQL

-- 1. Crear la tabla de conflictos si no existe
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
);

-- 2. Agregar columnas al wizard si no existen
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='contact_import_wizard' AND column_name='has_conflicts') THEN
        ALTER TABLE contact_import_wizard ADD COLUMN has_conflicts BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='contact_import_wizard' AND column_name='conflict_count') THEN
        ALTER TABLE contact_import_wizard ADD COLUMN conflict_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- 3. Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_conflict_wizard ON contact_import_conflict(wizard_id);
CREATE INDEX IF NOT EXISTS idx_conflict_partner ON contact_import_conflict(existing_partner_id);
