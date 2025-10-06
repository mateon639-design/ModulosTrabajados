# -*- coding: utf-8 -*-
from odoo import fields, models

class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    x_is_gradable = fields.Boolean("Calificable", help="Si está activo, la encuesta se califica al enviar.")
    x_min_score   = fields.Float("Puntaje mínimo", help="<=1: proporción. <=100: porcentaje. >100: puntos.")

class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    x_weight = fields.Float("Peso", default=1.0, help="Peso de la pregunta para el cálculo de nota.")
