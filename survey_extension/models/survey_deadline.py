# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_DEADLINE_CANDIDATES = ("response_deadline", "deadline", "date_deadline", "end_date", "date_end")

class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    # No creamos un campo nuevo; solo exponemos un boolean computado (no almacenado)
    deadline_passed = fields.Boolean(
        string="Vencida",
        compute="_compute_deadline_passed",
        store=False
    )

    def _get_deadline_value(self):
        """Devuelve el valor datetime del campo de fecha límite disponible en este build."""
        self.ensure_one()
        for name in _DEADLINE_CANDIDATES:
            if name in self._fields:
                return self[name]
        return False

    @api.depends(lambda self: [c for c in _DEADLINE_CANDIDATES if c in self._fields])
    def _compute_deadline_passed(self):
        now = fields.Datetime.now()
        for survey in self:
            dt = survey._get_deadline_value()
            survey.deadline_passed = bool(dt and dt < now)

    def _check_deadline_or_raise(self):
        self.ensure_one()
        dt = self._get_deadline_value()
        if dt and dt < fields.Datetime.now():
            # Mensaje solicitado
            raise UserError(_("La fecha límite de esta encuesta ya ha pasado, no es posible enviar respuestas."))


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.model_create_multi
    def create(self, vals_list):
        recs = []
        for vals in vals_list:
            survey_id = vals.get("survey_id")
            if survey_id:
                survey = self.env["survey.survey"].browse(survey_id)
                if survey.exists():
                    survey._check_deadline_or_raise()
            recs.append(super(SurveyUserInput, self).create([vals])[0])
        return self.browse([r.id for r in recs])

    def write(self, vals):
        going_done = "state" in vals and vals.get("state") == "done"

        # 1) Validación de fecha límite (tu lógica de la tarea 1)
        if going_done:
            for rec in self:
                if rec.survey_id:
                    rec.survey_id._check_deadline_or_raise()

        # 2) Ejecuta la escritura real
        res = super().write(vals)

        # 3) Si se cerró (done), calcular y guardar la nota
        if going_done:
            self._grade_user_inputs()

        return res

