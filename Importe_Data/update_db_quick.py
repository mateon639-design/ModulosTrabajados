# Script de actualización rápida de base de datos
# Ejecutar: python update_db_quick.py

import psycopg2

# Configuración - AJUSTAR SEGÚN TU CONFIGURACIÓN
DB_NAME = 'mateo'  # Nombre de tu base de datos
DB_USER = 'odoo'   # Usuario de PostgreSQL
DB_PASSWORD = 'odoo'  # Contraseña
DB_HOST = 'localhost'
DB_PORT = '5432'

def update_database():
    """Actualiza la base de datos con las nuevas columnas y tabla."""
    
    print("\n" + "="*70)
    print("ACTUALIZACIÓN RÁPIDA DE BASE DE DATOS - IMPORTE DATA")
    print("="*70)
    
    try:
        # Conectar a PostgreSQL
        print(f"\nConectando a la base de datos '{DB_NAME}'...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("✓ Conexión exitosa")
        
        # 1. Crear tabla de conflictos
        print("\n1. Creando tabla contact_import_conflict...")
        cursor.execute("""
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
        print("   ✓ Tabla creada/verificada")
        
        # 2. Agregar columna has_conflicts
        print("\n2. Agregando columna has_conflicts...")
        try:
            cursor.execute("""
                ALTER TABLE contact_import_wizard 
                ADD COLUMN has_conflicts BOOLEAN DEFAULT FALSE
            """)
            print("   ✓ Columna has_conflicts agregada")
        except psycopg2.errors.DuplicateColumn:
            print("   ✓ Columna has_conflicts ya existe")
            conn.rollback()
        
        # 3. Agregar columna conflict_count
        print("\n3. Agregando columna conflict_count...")
        try:
            cursor.execute("""
                ALTER TABLE contact_import_wizard 
                ADD COLUMN conflict_count INTEGER DEFAULT 0
            """)
            print("   ✓ Columna conflict_count agregada")
        except psycopg2.errors.DuplicateColumn:
            print("   ✓ Columna conflict_count ya existe")
            conn.rollback()
        
        # 4. Crear índices
        print("\n4. Creando índices...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conflict_wizard 
            ON contact_import_conflict(wizard_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conflict_partner 
            ON contact_import_conflict(existing_partner_id)
        """)
        print("   ✓ Índices creados")
        
        # Commit
        conn.commit()
        
        print("\n" + "="*70)
        print("✓ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\nPróximos pasos:")
        print("1. Refrescar el navegador (F5)")
        print("2. Ir a Importe Data > Importar Contactos")
        print("3. Probar la importación con detección de conflictos")
        print("="*70 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("\n" + "="*70)
        print("✗ ERROR")
        print("="*70)
        print(f"Error: {e}")
        print("\nSolución alternativa:")
        print("1. Desinstalar el módulo 'Importe Data' desde Odoo")
        print("2. Reinstalarlo completamente")
        print("="*70 + "\n")

if __name__ == '__main__':
    update_database()
