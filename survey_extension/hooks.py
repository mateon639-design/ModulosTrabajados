# -*- coding: utf-8 -*-
"""Rutinas de inicialización para completar códigos de encuestas existentes."""

from odoo import SUPERUSER_ID, api


def assign_survey_codes(cr, registry):
    """Asignar códigos faltantes o fuera de formato a encuestas previas."""

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["survey.survey"]._assign_missing_codes()
