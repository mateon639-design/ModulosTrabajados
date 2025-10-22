# -*- coding: utf-8 -*-
from odoo import http


class SurveyExtensionController(http.Controller):
    """Punto de entrada para endpoints HTTP personalizados relacionados con encuestas."""

    @http.route("/survey_extension/ping", type="json", auth="user")
    def ping(self):
        """Endpoint simple para validar que el módulo está operativo."""
        return {"status": "ok", "message": "Survey Extension online"}
    