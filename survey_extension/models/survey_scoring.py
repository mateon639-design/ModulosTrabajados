# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import isclose

# Compatibilidad con distintos nombres que pueda tener tu base
CALIFICABLE_CANDIDATES = ("calificable", "is_quiz", "is_scored", "gradable", "grade_enabled")
MIN_SCORE_CANDIDATES   = ("puntaje_minimo", "min_score", "minimum_score", "passing_score", "pass_score", "score_min")
WEIGHT_CANDIDATES      = ("peso", "weight", "points", "puntaje", "score_weight")


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    # --- Resultados guardados en la participación ---
    x_score_total    = fields.Float("Puntaje total", digits=(16, 4))
    x_score_obtained = fields.Float("Puntaje obtenido", digits=(16, 4))
    x_score_percent  = fields.Float("Porcentaje", digits=(16, 4))
    x_min_required   = fields.Float("Mínimo exigido (puntos)", digits=(16, 4))
    x_passed         = fields.Boolean("Aprobado")

    # --- Alias (related) para compatibilidad con vistas que usan otros nombres ---
    #     *Si tu vista usa estos nombres, no hace falta cambiarla.*
    score_points     = fields.Float(string="Puntaje obtenido", related="x_score_obtained", readonly=True)
    score_total      = fields.Float(string="Puntaje total",     related="x_score_total",     readonly=True)
    score_percentage = fields.Float(string="Porcentaje",        related="x_score_percent",   readonly=True)
    is_passed        = fields.Boolean(string="Aprobado",        related="x_passed",          readonly=True)

    # --- Helper para usar en vistas backend (mostrar/ocultar por si la encuesta es calificable) ---
    is_gradable_rel = fields.Boolean(
        string="Es calificable",
        compute="_compute_is_gradable_rel",
        store=False,
    )

    # =========================
    # Helpers internos
    # =========================
    def _get_value(self, record, names, default=None):
        """Devuelve el primer campo existente en 'names' desde 'record'."""
        for n in names:
            if n in record._fields:
                return record[n]
        return default

    def _get_question_weight(self, q):
        """Peso por pregunta. Si no hay campo de peso en tu modelo, asume 1.0."""
        for n in WEIGHT_CANDIDATES:
            if n in q._fields and q[n]:
                return float(q[n])
        return 1.0

    def _selected_answer_ids(self, line):
        """IDs seleccionados (soporta single y multiple choice)."""
        ids_ = set()
        if "suggested_answer_id" in line._fields and line.suggested_answer_id:
            ids_.add(line.suggested_answer_id.id)
        if "suggested_answer_ids" in line._fields and line.suggested_answer_ids:
            ids_.update(line.suggested_answer_ids.ids)
        return ids_

    def _correct_answer_ids(self, q):
        """IDs marcados como correctos en la pregunta."""
        ids_ = set()
        if "suggested_answer_ids" in q._fields:
            Answer = self.env["survey.question.answer"]
            if "is_correct" in Answer._fields:
                ids_.update(q.suggested_answer_ids.filtered("is_correct").ids)
        return ids_

    def _is_line_correct(self, line):
        """True/False/None (None = la pregunta no califica porque no define correctas)."""
        q = line.question_id
        correct_ids = self._correct_answer_ids(q)
        if not correct_ids:
            return None
        selected_ids = self._selected_answer_ids(line)
        if len(correct_ids) == 1:
            return selected_ids == correct_ids
        # multiple choice: debe coincidir exactamente
        return selected_ids == correct_ids

    def _compute_min_required_points(self, survey, total_points):
        """
        Interpreta el mínimo así:
          - <= 1.0  → proporción (0.7 = 70% del total)
          - <= 100  → porcentaje (70 = 70% del total)
          -  > 100  → puntos absolutos
        """
        raw = self._get_value(survey, MIN_SCORE_CANDIDATES, default=0.0) or 0.0
        try:
            mv = float(raw)
        except Exception:
            mv = 0.0

        if mv <= 1.0:
            return mv * total_points
        elif mv <= 100.0:
            return (mv / 100.0) * total_points
        else:
            return mv

    # =========================
    # Cómputos públicos
    # =========================
    @api.depends('survey_id')
    def _compute_is_gradable_rel(self):
        for ui in self:
            flag = False
            survey = ui.survey_id
            if survey:
                for name in CALIFICABLE_CANDIDATES:
                    if name in survey._fields and survey[name]:
                        flag = True
                        break
            ui.is_gradable_rel = flag

    def _grade_user_inputs(self):
        """
        Calcula y guarda la nota de cada participación cuando la encuesta es 'calificable'.
        Llamar este método al pasar la participación a state='done'.
        """
        for ui in self:
            survey = ui.survey_id
            if not survey:
                continue

            # ¿Encuesta marcada como calificable?
            is_calificable = False
            for name in CALIFICABLE_CANDIDATES:
                if name in survey._fields and survey[name]:
                    is_calificable = True
                    break
            if not is_calificable:
                continue  # no hacer nada si no es calificable

            total_points = 0.0
            obtained = 0.0

            for line in ui.user_input_line_ids:
                q = line.question_id
                if not q:
                    continue

                weight = self._get_question_weight(q)
                verdict = self._is_line_correct(line)

                if verdict is None:
                    continue  # pregunta sin correctas definidas → no puntúa

                total_points += weight
                if verdict:
                    obtained += weight

            percent = (obtained / total_points * 100.0) if total_points > 0 else 0.0
            min_req = self._compute_min_required_points(survey, total_points)
            passed = (obtained > min_req) or isclose(obtained, min_req, rel_tol=1e-9, abs_tol=1e-9)

            ui.write({
                "x_score_total": total_points,
                "x_score_obtained": obtained,
                "x_score_percent": percent,
                "x_min_required": min_req,
                "x_passed": passed,
            })
