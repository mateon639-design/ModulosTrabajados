# -*- coding: utf-8 -*-
"""Gestión de adjuntos vinculados a respuestas de encuestas."""

from odoo import _, fields, models


class SurveyUserInputAttachment(models.Model):
    _name = "survey.user_input.attachment"
    _description = "Adjunto de respuesta de encuesta"
    _order = "create_date asc, id asc"

    user_input_id = fields.Many2one(
        "survey.user_input",
        string="Participación",
        required=True,
        ondelete="cascade",
        index=True,
    )
    question_id = fields.Many2one(
        "survey.question",
        string="Pregunta",
        required=True,
        ondelete="cascade",
        index=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Archivo",
        required=True,
        ondelete="cascade",
        index=True,
    )
    line_id = fields.Many2one(
        "survey.user_input.line",
        string="Respuesta vinculada",
        ondelete="set null",
    )
    mimetype = fields.Char(related="attachment_id.mimetype", store=False, string="Tipo")
    name = fields.Char(related="attachment_id.name", store=False, string="Nombre")
    question_display_name = fields.Char(
        string="Pregunta",
        compute="_compute_question_display_name",
        store=False,
    )

    _sql_constraints = [
        (
            "survey_user_input_attachment_unique",
            "unique(user_input_id, question_id, attachment_id)",
            "Este archivo ya está asociado a la pregunta seleccionada.",
        )
    ]

    def name_get(self):
        result = []
        for record in self:
            display = record.attachment_id.display_name or record.attachment_id.name or _("Archivo")
            result.append((record.id, display))
        return result

    def unlink(self):
        attachments = self.mapped("attachment_id")
        res = super().unlink()
        attachments.sudo().unlink()
        return res

    def action_download(self):
        self.ensure_one()
        if not self.attachment_id:
            return False
        return {
            "type": "ir.actions.act_url",
            "name": self.attachment_id.display_name or self.attachment_id.name,
            "target": "self",
            "url": f"/web/content/{self.attachment_id.id}?download=1",
        }

    def _compute_question_display_name(self):
        for record in self:
            record.question_display_name = record.question_id.display_name if record.question_id else False


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    attachment_link_ids = fields.One2many(
        "survey.user_input.attachment",
        "user_input_id",
        string="Adjuntos",
    )

    def get_question_attachments(self, question):
        self.ensure_one()
        if not question:
            return self.env["survey.user_input.attachment"]
        return self.attachment_link_ids.filtered(lambda link: link.question_id == question)

    def _save_lines(self, question, answer, comment=None, overwrite_existing=True):
        # Manejar tipos WPM primero
        if question.question_type in ('wpm_reading', 'wpm_typing'):
            return self._save_line_wpm(question, answer, comment)
        
        if question.question_type in ("instruction", "file_upload"):
            existing = self.user_input_line_ids.filtered(lambda line: line.question_id == question)
            if question.question_type == "instruction":
                if existing:
                    existing.unlink()
                return existing

            attachment_count = question._extension_attachment_count(answer)
            if attachment_count > 0:
                if existing:
                    existing.unlink()
                return existing

            if existing:
                existing.write({"skipped": True, "answer_type": False})
            else:
                self.env["survey.user_input.line"].create(
                    {
                        "user_input_id": self.id,
                        "question_id": question.id,
                        "skipped": True,
                        "answer_type": False,
                    }
                )
            return existing

        return super()._save_lines(question, answer, comment, overwrite_existing)
    
    def _save_line_wpm(self, question, answer, comment=None):
        """
        Guardar respuestas de preguntas tipo WPM (Words Per Minute).
        Maneja tanto wpm_reading como wpm_typing.
        """
        self.ensure_one()
        
        # Verificar si la prueba fue completada
        question_prefix = f"{question.id}_"
        wpm_completed = False
        
        if isinstance(answer, dict):
            completed_key = f"{question_prefix}wpm_completed"
            wpm_completed = answer.get(completed_key) == '1'
        
        # Si NO se completó la prueba, marcar como omitida
        if not wpm_completed:
            existing_line = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', question.id)
            ], limit=1)
            
            if existing_line:
                existing_line.write({'skipped': True, 'answer_type': False})
                return existing_line
            else:
                return self.env['survey.user_input.line'].create({
                    'user_input_id': self.id,
                    'question_id': question.id,
                    'skipped': True,
                    'answer_type': False,
                })
        
        # Si SÍ se completó, procesar los datos WPM
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'answer_type': 'text_box',
            'skipped': False,
        }
        
        # Extraer datos WPM del formulario
        wpm_time = 0
        wpm_words = 0
        wpm_text = ""
        
        if isinstance(answer, dict):
            for key, value in answer.items():
                if key.startswith(question_prefix):
                    suffix = key.replace(question_prefix, '')
                    
                    if suffix == 'answer_text' and value:
                        wpm_text = value
                        vals['wpm_typed_text'] = value
                        vals['value_text_box'] = value
                    elif suffix == 'wpm_time' and value:
                        wpm_time = float(value)
                        vals['wpm_time_seconds'] = wpm_time
                    elif suffix == 'wpm_words' and value:
                        wpm_words = int(value)
                        vals['wpm_word_count'] = wpm_words
                    elif suffix == 'wpm_start' and value:
                        try:
                            from datetime import datetime
                            vals['wpm_start_time'] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass
                    elif suffix == 'wpm_end' and value:
                        try:
                            from datetime import datetime
                            vals['wpm_end_time'] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass
        
        # Para wpm_reading, el texto viene del campo de la pregunta
        if question.question_type == 'wpm_reading':
            vals['value_text_box'] = question.wpm_reading_text or ''
        
        # Si no hay tiempo válido, marcar como omitida
        if wpm_time == 0 or (question.question_type == 'wpm_typing' and not wpm_text):
            vals['skipped'] = True
        
        # Buscar línea existente
        existing_line = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ], limit=1)
        
        if existing_line:
            existing_line.write(vals)
            return existing_line
        else:
            return self.env['survey.user_input.line'].create(vals)

