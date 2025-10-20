# -*- coding: utf-8 -*-
"""Rutinas de inicialización para completar códigos de encuestas existentes."""

from odoo import SUPERUSER_ID, api


def assign_survey_codes(cr, registry):
    """Asignar códigos faltantes o fuera de formato a encuestas previas."""

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["survey.survey"]._assign_missing_codes()


def migrate_version_year_to_char(cr, registry):
    """Migra el campo version_year de Integer a Char para evitar formato con separadores."""
    
    # Verificar si la columna existe y tiene tipo numérico
    cr.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'survey_survey' 
        AND column_name = 'version_year'
    """)
    
    result = cr.fetchone()
    if result and result[1] in ('integer', 'numeric', 'bigint'):
        # Convertir valores existentes a string
        cr.execute("""
            ALTER TABLE survey_survey 
            ALTER COLUMN version_year TYPE varchar(4) 
            USING CASE 
                WHEN version_year IS NULL THEN NULL 
                ELSE version_year::varchar 
            END
        """)
