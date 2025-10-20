# -*- coding: utf-8 -*-
"""Asistente para generar nuevas versiones de encuestas."""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveyVersionWizard(models.TransientModel):
    _name = "survey.version.wizard"
    _description = "Asistente de versionado de encuestas"

    survey_id = fields.Many2one(
        "survey.survey",
        string="Encuesta origen",
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get("default_survey_id"),
    )
    version_date = fields.Date(
        string="Fecha de versión",
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help="Fecha que identifica la versión generada.",
    )
    new_title = fields.Char(
        string="Título de la nueva versión",
        required=True,
        help="Nombre que tendrá la encuesta duplicada.",
    )
    title_is_custom = fields.Boolean(
        string="Título personalizado",
        default=False,
        help="Bandera interna para saber si el usuario modificó el título sugerido.",
    )
    question_line_ids = fields.One2many(
        "survey.version.wizard.line",
        "wizard_id",
        string="Preguntas",
        help="Preguntas disponibles para conservar en la nueva versión.",
    )

    @api.model
    def default_get(self, fields_list):
        """Inicializa el wizard con los valores predeterminados y las líneas de preguntas."""
        result = super().default_get(fields_list)
        survey = None
        default_survey_id = self.env.context.get("default_survey_id") or self.env.context.get("active_id")
        if default_survey_id:
            survey = self.env["survey.survey"].browse(default_survey_id)
        if survey and survey.exists():
            result.setdefault("survey_id", survey.id)
            date_today = fields.Date.context_today(self)
            result.setdefault("version_date", date_today)
            suggested = self._build_suggested_title_static(survey, date_today)
            if suggested:
                result.setdefault("new_title", suggested)
            else:
                result.setdefault("new_title", survey.title)
            result.setdefault("title_is_custom", False)
            
            # Preparar líneas de preguntas usando el comando (0, 0, vals)
            if "question_line_ids" in fields_list or not fields_list:
                questions = survey.question_and_page_ids.filtered(lambda q: not q.is_page)
                questions = questions.sorted(key=lambda q: (
                    q.page_id.sequence if q.page_id else -1,
                    q.sequence,
                    q.id,
                ))
                
                line_vals = []
                for question in questions:
                    line_vals.append((0, 0, {
                        "question_id": question.id,
                        "include": True,
                    }))
                
                if line_vals:
                    result["question_line_ids"] = line_vals
        
        return result

    @staticmethod
    def _build_suggested_title_static(survey, date_value):
        """Genera un título sugerido con base en la fecha y el nombre de la encuesta."""
        if not survey or not survey.title:
            return False
        if not date_value:
            return survey.title
        date_obj = fields.Date.to_date(date_value)
        if not date_obj:
            return survey.title
        return ("%s %s" % (survey.title, date_obj.year)).strip()

    def _build_suggested_title(self):
        self.ensure_one()
        return self._build_suggested_title_static(self.survey_id, self.version_date or fields.Date.context_today(self))

    @api.onchange("version_date")
    def _onchange_version_date(self):
        for wizard in self:
            suggested = wizard._build_suggested_title()
            if not wizard.title_is_custom and suggested:
                wizard.new_title = suggested

    @api.onchange("new_title")
    def _onchange_new_title(self):
        for wizard in self:
            suggested = wizard._build_suggested_title()
            clean_title = (wizard.new_title or "").strip()
            wizard.title_is_custom = bool(clean_title and suggested and clean_title != suggested)

    def action_confirm(self):
        self.ensure_one()
        if not self.question_line_ids:
            raise ValidationError(_("No se encontraron preguntas para versionar."))
        selected_lines = self.question_line_ids.filtered("include")
        if not selected_lines:
            raise ValidationError(_("Selecciona al menos una pregunta para crear la nueva versión."))
        survey = self.survey_id
        if not survey:
            raise ValidationError(_("No se encontró la encuesta original."))
        clean_title = (self.new_title or "").strip()
        if not clean_title:
            raise ValidationError(_("Define el título de la nueva versión."))

        default_vals = {
            "title": clean_title,
            "version_date": self.version_date,
        }
        new_survey = survey.copy(default=default_vals)

        allowed_ids = set(selected_lines.question_id.ids)
        original_questions = survey.question_ids.sorted(key=lambda q: (
            q.page_id.sequence if q.page_id else -1,
            q.sequence,
            q.id,
        ))
        cloned_questions = new_survey.question_ids.sorted(key=lambda q: (
            q.page_id.sequence if q.page_id else -1,
            q.sequence,
            q.id,
        ))
        for original, cloned in zip(original_questions, cloned_questions):
            if original.id not in allowed_ids:
                cloned.unlink()

        pages_to_check = new_survey.question_and_page_ids.filtered("is_page")
        for page in pages_to_check:
            related = new_survey.question_ids.filtered(lambda q: q.page_id.id == page.id)
            if not related:
                page.unlink()

        return {
            "type": "ir.actions.act_window",
            "name": _("Nueva versión"),
            "res_model": "survey.survey",
            "view_mode": "form",
            "res_id": new_survey.id,
            "target": "current",
        }


class SurveyVersionWizardLine(models.TransientModel):
    _name = "survey.version.wizard.line"
    _description = "Línea del asistente de versionado"
    _rec_name = "question_title"

    wizard_id = fields.Many2one(
        "survey.version.wizard",
        string="Wizard",
        ondelete="cascade",
    )
    question_id = fields.Many2one(
        "survey.question",
        string="Pregunta",
        required=True,
        readonly=True,
    )
    include = fields.Boolean(
        string="Conservar",
        default=True,
    )
    question_title = fields.Char(
        string="Título",
        related="question_id.title",
        readonly=True,
    )
    page_title = fields.Char(
        string="Sección",
        compute="_compute_page_title",
        readonly=True,
        store=False,
    )
    question_type = fields.Selection(
        related="question_id.question_type",
        string="Tipo",
        readonly=True,
    )

    @api.depends("question_id", "question_id.page_id")
    def _compute_page_title(self):
        for line in self:
            line.page_title = line.question_id.page_id.title if line.question_id.page_id else False

    @api.model_create_multi
    def create(self, vals_list):
        """Asegura que wizard_id esté presente al crear líneas."""
        # Si se crea desde el contexto del wizard, obtener el ID
        wizard_id_from_context = self.env.context.get('default_wizard_id')
        
        for vals in vals_list:
            # Si no tiene wizard_id pero hay uno en el contexto, usarlo
            if not vals.get('wizard_id') and wizard_id_from_context:
                vals['wizard_id'] = wizard_id_from_context
        
        return super().create(vals_list)

    def write(self, vals):
        """Permite escribir sin requerir wizard_id si ya existe."""
        return super().write(vals)
