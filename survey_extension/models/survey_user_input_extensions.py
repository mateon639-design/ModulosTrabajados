# -*- coding: utf-8 -*-
"""Extiende survey.user_input para:
- Asociar respuestas a un dispositivo (tablet) vía device_id / device_uuid.
- Calcular y mostrar la duración real de la participación.
- Mantener la métrica de última actividad del dispositivo.
"""

from odoo import _, api, fields, models

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    # --- Dispositivo ---
    device_id = fields.Many2one(
        'survey.device',
        string='Dispositivo (Tablet)',
        ondelete='set null'
    )
    device_uuid = fields.Char(
        string='UUID del dispositivo',
        help='Identificador único del dispositivo que respondió',
        index=True,
    )

    # --- Métricas de duración ---
    x_survey_duration = fields.Float(
        string='Duración (segundos)',
        help='Duración en segundos entre el inicio y fin de la participación.',
        compute='_compute_x_survey_duration',
        store=True,
    )
    x_survey_duration_display = fields.Char(
        string='Tiempo de respuesta',
        help='Duración expresada en un formato legible (minutos/horas).',
        compute='_compute_x_survey_duration_display',
    )

    # ----------------------------
    # Creación y actualización
    # ----------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # Normalizar device_uuid (si viene vacío a None)
        for vals in vals_list:
            if 'device_uuid' in vals and vals['device_uuid']:
                vals['device_uuid'] = str(vals['device_uuid']).strip() or False

        records = super().create(vals_list)

        # Actualizar última actividad del dispositivo si aplica
        for rec in records:
            if rec.device_id:
                rec.device_id.update_last_response()
        return records

    def write(self, vals):
        # Normalizar device_uuid si se actualiza
        if 'device_uuid' in vals and vals['device_uuid']:
            vals['device_uuid'] = str(vals['device_uuid']).strip() or False

        res = super().write(vals)

        # Si cambia el dispositivo, el estado o la fecha de fin, refrescamos actividad
        fields_that_imply_activity = {'device_id', 'state', 'end_datetime'}
        if fields_that_imply_activity.intersection(vals.keys()):
            for rec in self:
                if rec.device_id:
                    rec.device_id.update_last_response()
        return res

    # ----------------------------
    # Computes de duración
    # ----------------------------
    @api.depends('start_datetime', 'end_datetime')
    def _compute_x_survey_duration(self):
        for rec in self:
            duration = 0.0
            start = rec.start_datetime
            end = rec.end_datetime
            # start_datetime / end_datetime ya son datetime; defensas básicas:
            if start and end:
                try:
                    # Asegurar que end >= start
                    delta = end - start
                    duration = max(delta.total_seconds(), 0.0)
                except Exception:
                    duration = 0.0
            rec.x_survey_duration = duration

    @api.depends('x_survey_duration')
    def _compute_x_survey_duration_display(self):
        for rec in self:
            rec.x_survey_duration_display = rec._format_duration_for_display(rec.x_survey_duration)

    # ----------------------------
    # Utilidad
    # ----------------------------
    def _format_duration_for_display(self, seconds):
        """Renderiza la duración en una cadena legible en español."""
        if not seconds or seconds <= 0:
            return _('Sin registrar')

        total_seconds = int(round(seconds))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds_remaining = total_seconds % 60

        parts = []
        if hours:
            parts.append(_('1 hora') if hours == 1 else _('%s horas') % hours)
        if minutes:
            parts.append(_('1 minuto') if minutes == 1 else _('%s minutos') % minutes)
        if seconds_remaining:
            parts.append(_('1 segundo') if seconds_remaining == 1 else _('%s segundos') % seconds_remaining)

        if not parts:
            parts.append(_('1 segundo'))

        return ' '.join(parts)
