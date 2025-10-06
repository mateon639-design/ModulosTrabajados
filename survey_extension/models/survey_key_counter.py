# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    key_question_count = fields.Integer(
        string="Preguntas clave",
        compute="_compute_key_question_count",
        store=True,
        readonly=True,
        help="Cantidad de preguntas marcadas como clave en esta encuesta.",
    )

    @api.depends('question_ids.is_key')
    def _compute_key_question_count(self):
        """Cuenta preguntas clave por encuesta de forma vectorizada (read_group)."""
        surveys = self.filtered(lambda s: s.id)
        counts_map = {sid: 0 for sid in surveys.ids}
        if surveys:
            data = self.env['survey.question'].read_group(
                domain=[('survey_id', 'in', surveys.ids), ('is_key', '=', True)],
                fields=['survey_id'],
                groupby=['survey_id'],
                lazy=False,
            )
            for row in data:
                # En v17/v18 read_group devuelve survey_id (id, display_name) y <field>_count o __count
                sid = row['survey_id'][0] if row.get('survey_id') else False
                if sid:
                    counts_map[sid] = row.get('survey_id_count', row.get('__count', 0))

        for rec in self:
            rec.key_question_count = counts_map.get(rec.id, 0)
