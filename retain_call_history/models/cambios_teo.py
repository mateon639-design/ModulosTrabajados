# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CambiosTeo(models.Model):
    _name = "cambios.teo"
    _description = "Mini curso de IA (Cambios TEO)"
    _order = "create_date desc"

    name = fields.Char(string="Título del curso", required=True, default="Introducción rápida a IA")
    description = fields.Html(string="Contenido del curso", sanitize=True)
    video_url = fields.Char(string="URL de video (opcional)")

    question_ids = fields.One2many("cambios.teo.question", "course_id", string="Preguntas")
    attempt_ids = fields.One2many("cambios.teo.attempt", "course_id", string="Intentos")
    pass_score = fields.Integer(string="Puntaje mínimo (aprobación)", default=70)

    # vínculo opcional con el registro del formulario objetivo (ej. retain.call.history)
    target_model = fields.Char(
        string="Modelo objetivo",
        help="Nombre técnico del modelo donde se inserta la pestaña (ej. retain.call.history)",
    )
    target_res_id = fields.Integer(string="ID del registro objetivo")

    def action_generate_quick_content(self):
        """Crea contenido y preguntas base si está vacío: curso express."""
        for course in self:
            if not course.description:
                course.description = """
                <h3>¿Qué es la IA Generativa?</h3>
                <p>La IA generativa crea contenido nuevo (texto, voz, imágenes) a partir de datos de entrenamiento usando redes neuronales.</p>
                <ul>
                  <li>Casos: asistentes, análisis de llamadas, FAQ inteligentes.</li>
                  <li>Riesgos: alucinaciones, sesgos, privacidad.</li>
                  <li>Buenas prácticas: verificación humana, datos limpios, trazabilidad.</li>
                </ul>
                """
            if not course.question_ids:
                course.question_ids = [(0, 0, {
                    "name": "La IA generativa puede crear contenido nuevo a partir de datos.",
                    "answer_type": "single",
                    "option_a": "Verdadero",
                    "option_b": "Falso",
                    "correct_single": "a",
                    "explanation": "¡Correcto! Ese es su objetivo principal."
                }), (0, 0, {
                    "name": "Selecciona buenas prácticas al usar IA generativa:",
                    "answer_type": "multiple",
                    "option_a": "Verificar con humanos",
                    "option_b": "Ignorar sesgos",
                    "option_c": "Cuidar privacidad de datos",
                    "correct_multiple": "a,c",
                    "explanation": "Verificación humana y privacidad son clave."
                })]

    def action_open_quiz(self):
        """Convenience action para abrir el formulario del curso en vista form."""
        return {
            "type": "ir.actions.act_window",
            "name": _("Curso IA (Cambios TEO)"),
            "res_model": "cambios.teo",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }


class CambiosTeoQuestion(models.Model):
    _name = "cambios.teo.question"
    _description = "Pregunta del Curso IA"

    course_id = fields.Many2one("cambios.teo", required=True, ondelete="cascade")
    name = fields.Char(string="Pregunta", required=True)
    answer_type = fields.Selection([
        ("single", "Selección única"),
        ("multiple", "Selección múltiple"),
        ("open", "Respuesta abierta"),
    ], default="single", required=True)

    # Opciones para single/multiple (A–D)
    option_a = fields.Char(string="Opción A")
    option_b = fields.Char(string="Opción B")
    option_c = fields.Char(string="Opción C")
    option_d = fields.Char(string="Opción D")

    # Respuesta correcta
    correct_single = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        string="Correcta (single)"
    )
    correct_multiple = fields.Char(
        string="Correctas (multiple)",
        help="Ej: a,c  (separadas por coma)"
    )

    # Explicación o retroalimentación
    explanation = fields.Text(string="Explicación/feedback")

    @api.constrains("answer_type", "correct_single", "correct_multiple")
    def _check_correctness_fields(self):
        for r in self:
            if r.answer_type == "single" and not r.correct_single:
                raise ValidationError(_("Define 'Correcta (single)' para preguntas de selección única."))
            if r.answer_type == "multiple" and not r.correct_multiple:
                raise ValidationError(_("Define 'Correctas (multiple)' (ej: a,c)."))


class CambiosTeoAttempt(models.Model):
    _name = "cambios.teo.attempt"
    _description = "Intento de Quiz IA"
    _order = "create_date desc"

    course_id = fields.Many2one("cambios.teo", required=True, ondelete="cascade")
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user, required=True)
    line_ids = fields.One2many("cambios.teo.attempt.line", "attempt_id", string="Respuestas")
    score = fields.Integer(string="Puntaje (%)", compute="_compute_score", store=True)
    approved = fields.Boolean(string="Aprobado", compute="_compute_score", store=True)

    @api.depends("line_ids.is_correct", "course_id.pass_score", "line_ids")
    def _compute_score(self):
        for att in self:
            total = len(att.line_ids)
            correct = len(att.line_ids.filtered(lambda l: l.is_correct))
            att.score = int((correct / total) * 100) if total else 0
            att.approved = att.score >= (att.course_id.pass_score or 70)

    def action_fill_all(self):
        """Genera líneas de respuesta vacías para todas las preguntas del curso (si no existen)."""
        for att in self:
            existing_q = att.line_ids.mapped("question_id").ids
            to_create = att.course_id.question_ids.filtered(lambda q: q.id not in existing_q)
            vals = []
            for q in to_create:
                vals.append((0, 0, {"question_id": q.id}))
            if vals:
                att.write({"line_ids": vals})

    def action_validate(self):
        """Valida respuestas (marca is_correct en las líneas)."""
        for att in self:
            for line in att.line_ids:
                line._compute_is_correct()


class CambiosTeoAttemptLine(models.Model):
    _name = "cambios.teo.attempt.line"
    _description = "Respuesta de Pregunta"

    attempt_id = fields.Many2one("cambios.teo.attempt", required=True, ondelete="cascade")
    question_id = fields.Many2one("cambios.teo.question", required=True)
    # Respuestas ingresadas por el usuario
    answer_single = fields.Selection([("a","A"),("b","B"),("c","C"),("d","D")], string="Respuesta (single)")
    answer_multiple = fields.Char(string="Respuestas (multiple)", help="Ej: a,c")
    answer_open = fields.Text(string="Respuesta abierta")

    is_correct = fields.Boolean(string="¿Correcta?", compute="_compute_is_correct", store=True)

    @api.depends("answer_single", "answer_multiple", "answer_open", "question_id.answer_type",
                 "question_id.correct_single", "question_id.correct_multiple")
    def _compute_is_correct(self):
        for l in self:
            q = l.question_id
            if not q:
                l.is_correct = False
                continue
            if q.answer_type == "single":
                l.is_correct = bool(l.answer_single and l.answer_single == q.correct_single)
            elif q.answer_type == "multiple":
                # normaliza
                def norm(s):
                    return ",".join(sorted({x.strip().lower() for x in (s or "").split(",") if x.strip()}))
                l.is_correct = norm(l.answer_multiple) == norm(q.correct_multiple)
            else:
                # abiertas: por defecto no se corrigen automáticamente
                l.is_correct = False
