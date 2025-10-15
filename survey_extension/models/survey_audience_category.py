# -*- coding: utf-8 -*-
from odoo import models, fields

class SurveyAudienceCategory(models.Model):
    _name = "survey.audience.category"
    _description = "Survey Audience Category"
    _rec_name = "name"
    _order = "sequence, name"

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    color = fields.Integer(
        string="Color Index",
        help="Índice de color (0..11) para tags."
    )
    active = fields.Boolean(default=True)

    # inversa técnica si quieres navegar desde la categoría a las encuestas
    survey_ids = fields.Many2many(
        "survey.survey",
        "survey_survey_audience_category_rel",
        "category_id",
        "survey_id",
        string="Encuestas"
    )
