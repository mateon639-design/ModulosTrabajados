# -*- coding: utf-8 -*-
# models/survey_calificacion_average.py
from odoo import api, fields, models

class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    participation_rate = fields.Float(
        string="Tasa de participación (%)",
        compute="_compute_survey_metrics",
        compute_sudo=True,
        digits=(16, 2),
    )
    average_score = fields.Float(
        string="Promedio de calificación (%)",
        compute="_compute_survey_metrics",
        compute_sudo=True,
        digits=(16, 2),
        help="Promedio de nota (en %) de las participaciones entregadas. "
             "Se calcula solo si la encuesta es calificable.",
    )

    # ---------------------------------------------------------------------
    # Cómputo de métricas
    # ---------------------------------------------------------------------
    @api.depends('user_input_ids.state', 'is_gradable')
    def _compute_survey_metrics(self):
        UI = self.env['survey.user_input'].sudo()

        # Detectar nombres de campos de puntaje/porcentaje disponibles
        score_percent_field = None
        for name in ('x_score_percent', 'score_percentage'):
            if name in UI._fields:
                score_percent_field = name
                break

        for survey in self:
            # Dominio base: participaciones de esta encuesta
            base_domain = [('survey_id', '=', survey.id)]
            if 'test_entry' in UI._fields:
                base_domain.append(('test_entry', '=', False))

            total_invited = UI.search_count(base_domain)
            done_domain = base_domain + [('state', '=', 'done')]
            total_done = UI.search_count(done_domain)

            # Tasa de participación
            rate = (total_done / total_invited * 100.0) if total_invited else 0.0

            # Promedio de calificación (si es calificable y hay entregas)
            avg = 0.0
            if survey.is_gradable and total_done:
                if score_percent_field:
                    # Usar directamente el porcentaje guardado en user_input
                    data = UI.read_group(done_domain, [f'{score_percent_field}:avg'], [])
                    avg = (data[0].get(f'{score_percent_field}_avg') or 0.0) if data else 0.0
                else:
                    # Fallback: calcular a partir de (obtenido/total)*100 si existen
                    got_field = None
                    tot_field = None
                    for n in ('x_score_obtained', 'score_points'):
                        if n in UI._fields:
                            got_field = n
                            break
                    for n in ('x_score_total', 'score_total'):
                        if n in UI._fields:
                            tot_field = n
                            break

                    if got_field and tot_field:
                        recs = UI.search(done_domain)
                        acc = 0.0
                        cnt = 0
                        for ui in recs:
                            total = getattr(ui, tot_field, 0.0) or 0.0
                            got = getattr(ui, got_field, 0.0) or 0.0
                            if total:
                                acc += (got / total) * 100.0
                                cnt += 1
                        avg = (acc / cnt) if cnt else 0.0

            survey.participation_rate = rate
            survey.average_score = avg
