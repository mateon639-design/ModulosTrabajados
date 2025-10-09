# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import sql

class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    x_is_gradable = fields.Boolean(
        string="Calificable (legado)",
        compute="_compute_x_is_gradable",
        inverse="_inverse_x_is_gradable",
        store=True,
        help="Campo histórico mantenido para compatibilidad. Usa 'Calificable' en su lugar.",
    )
    x_min_score = fields.Float(
        string="Puntaje mínimo (legado)",
        compute="_compute_x_min_score",
        inverse="_inverse_x_min_score",
        store=True,
        help="Campo histórico mantenido para compatibilidad. Usa 'Puntaje mínimo'.",
    )

    @api.depends('is_gradable')
    def _compute_x_is_gradable(self):
        for survey in self:
            survey.x_is_gradable = bool(survey.is_gradable)

    def _inverse_x_is_gradable(self):
        for survey in self:
            survey.is_gradable = bool(survey.x_is_gradable)

    @api.depends('min_score')
    def _compute_x_min_score(self):
        for survey in self:
            survey.x_min_score = survey.min_score

    def _inverse_x_min_score(self):
        for survey in self:
            survey.min_score = survey.x_min_score

    def init(self):
        super().init()
        cr = self.env.cr
        # Copiamos valores legacy hacia los campos nuevos una única vez (upgrade/install)
        if sql.column_exists(cr, 'survey_survey', 'x_is_gradable') and sql.column_exists(cr, 'survey_survey', 'is_gradable'):
            cr.execute("UPDATE survey_survey SET is_gradable = COALESCE(x_is_gradable, is_gradable)")
        if sql.column_exists(cr, 'survey_survey', 'x_min_score') and sql.column_exists(cr, 'survey_survey', 'min_score'):
            cr.execute("UPDATE survey_survey SET min_score = COALESCE(x_min_score, min_score)")

class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    x_weight = fields.Float(
        string="Peso (legado)",
        compute="_compute_x_weight",
        inverse="_inverse_x_weight",
        store=True,
        help="Campo histórico mantenido para compatibilidad. Usa 'Peso de la pregunta'.",
    )

    @api.depends('weight')
    def _compute_x_weight(self):
        for question in self:
            question.x_weight = question.weight

    def _inverse_x_weight(self):
        for question in self:
            question.weight = question.x_weight or 0.0

    def init(self):
        super().init()
        cr = self.env.cr
        if sql.column_exists(cr, 'survey_question', 'x_weight') and sql.column_exists(cr, 'survey_question', 'weight'):
            cr.execute("UPDATE survey_question SET weight = COALESCE(x_weight, weight)")
