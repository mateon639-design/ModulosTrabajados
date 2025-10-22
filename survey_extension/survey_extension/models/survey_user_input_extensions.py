# -*- coding: utf-8 -*-
"""Extiende survey.user_input para calcular y mostrar la duración real de la participación."""

from odoo import _, api, fields, models


class SurveyUserInputExtensions(models.Model):
    _inherit = 'survey.user_input'

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

    @api.depends('start_datetime', 'end_datetime')
    def _compute_x_survey_duration(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime:
                try:
                    # fields.Datetime are naive strings; use to_datetime to compute
                    start = fields.Datetime.to_datetime(rec.start_datetime)
                    end = fields.Datetime.to_datetime(rec.end_datetime)
                    if start and end:
                        rec.x_survey_duration = max((end - start).total_seconds(), 0.0)
                    else:
                        rec.x_survey_duration = 0.0
                except Exception:
                    rec.x_survey_duration = 0.0
            else:
                rec.x_survey_duration = 0.0

    @api.depends('x_survey_duration')
    def _compute_x_survey_duration_display(self):
        for rec in self:
            rec.x_survey_duration_display = rec._format_duration_for_display(rec.x_survey_duration)

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
