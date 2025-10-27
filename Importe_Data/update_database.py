# -*- coding: utf-8 -*-
"""
Script de actualización manual para Importe Data
Ejecutar desde el shell de Odoo con:

from importe_data.update_database import update_database
update_database(env)
"""

def update_database(env):
    """Actualiza la base de datos con las nuevas estructuras."""
    
    cr = env.cr
    
    print("\n" + "="*70)
    print("ACTUALIZACIÓN DE BASE DE DATOS - IMPORTE DATA")
    print("="*70)
    
    try:
        # 1. Crear la tabla de conflictos si no existe
        print("\n1. Verificando tabla contact_import_conflict...")
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
        print("   ✓ Tabla contact_import_conflict creada/verificada")
        
        # 2. Agregar columna has_conflicts
        print("\n2. Verificando columna has_conflicts...")
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
            print("   ✓ Columna has_conflicts agregada")
        else:
            print("   ✓ Columna has_conflicts ya existe")
        
        # 3. Agregar columna conflict_count
        print("\n3. Verificando columna conflict_count...")
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
            print("   ✓ Columna conflict_count agregada")
        else:
            print("   ✓ Columna conflict_count ya existe")
        
        # 4. Crear índices
        print("\n4. Creando índices...")
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_conflict_wizard 
            ON contact_import_conflict(wizard_id)
        """)
        print("   ✓ Índice idx_conflict_wizard creado")
        
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_conflict_partner 
            ON contact_import_conflict(existing_partner_id)
        """)
        print("   ✓ Índice idx_conflict_partner creado")
        
        # 5. Commit de los cambios
        cr.commit()
        
        print("\n" + "="*70)
        print("✓ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\nAhora puedes:")
        print("1. Refrescar el navegador (F5)")
        print("2. Ir a Importe Data > Importar Contactos")
        print("3. Usar la nueva funcionalidad de resolución de conflictos")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        cr.rollback()
        print("\n" + "="*70)
        print("✗ ERROR EN LA ACTUALIZACIÓN")
        print("="*70)
        print(f"Error: {e}")
        print("\nIntenta:")
        print("1. Desinstalar el módulo completamente")
        print("2. Reinstalarlo desde cero")
        print("="*70 + "\n")
        return False

if __name__ == '__main__':
    print("\nEste script debe ejecutarse dentro del shell de Odoo:")
    print("\nComando:")
    print("  odoo-bin shell -d <nombre_base_datos> -c <archivo_config>")
    print("\nDentro del shell de Odoo, ejecutar:")
    print("  >>> from importe_data.update_database import update_database")
    print("  >>> update_database(env)")
