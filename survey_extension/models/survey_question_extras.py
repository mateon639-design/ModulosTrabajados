# -*- coding: utf-8 -*-
from odoo import fields, models

class SurveyQuestionCategory(models.Model):
    _name = "survey.question.category"
    _description = "Categoría de pregunta de encuesta"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)

class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    weight = fields.Float(
        string="Peso de la pregunta",
        default=1.0,
        help="Importancia relativa. 2.0 equivale al doble que 1.0."
    )
    category_id = fields.Many2one(
        "survey.question.category",
        string="Categoría",
        help="Clasifica la pregunta (p. ej.: Técnica, Actitudinal, General)."
    )
    is_key = fields.Boolean(
        string="¿Es pregunta clave?",
        help="Marca si esta pregunta es clave dentro de la encuesta."
    )
