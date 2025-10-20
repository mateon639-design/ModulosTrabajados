# -*- coding: utf-8 -*-
"""Controladores adicionales para gestionar adjuntos dentro de las encuestas."""

import base64

from odoo import http
from odoo.addons.survey.controllers.main import Survey as SurveyController
from odoo.http import request


class SurveyAttachmentController(SurveyController):
    """Expone rutas públicas (tokenizadas) para subir y eliminar adjuntos."""

    _upload_size_param = "survey_extension.max_upload_size_mb"

    def _can_handle_request(self, survey_token, answer_token, require_editable=True):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data["validity_code"] is not True:
            return None, None, request.make_json_response({"error": access_data["validity_code"]}, status=403)

        survey = access_data["survey_sudo"]
        answer = access_data["answer_sudo"]
        if not answer:
            return None, None, request.make_json_response({"error": "no_answer"}, status=404)
        if require_editable and answer.state == "done":
            return None, None, request.make_json_response({"error": "readonly"}, status=400)
        return survey, answer, None

    @http.route(
        "/survey_extension/attachment/upload",
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=True,
    )
    def upload_attachment(self, survey_token, answer_token, question_id, **kwargs):
        survey, answer, error_response = self._can_handle_request(survey_token, answer_token)
        if error_response:
            return error_response

        try:
            question_id_int = int(question_id)
        except (TypeError, ValueError):
            return request.make_json_response({"error": "invalid_question"}, status=400)

        question = survey.question_ids.filtered(lambda q: q.id == question_id_int)
        if not question:
            return request.make_json_response({"error": "invalid_question"}, status=404)

        files = request.httprequest.files.getlist("file")
        if not files:
            return request.make_json_response({"error": "missing_file"}, status=400)

        max_size_mb = int(
            request.env["ir.config_parameter"].sudo().get_param(self._upload_size_param, default=25)
        )
        Attachment = request.env["ir.attachment"].sudo()
        Link = request.env["survey.user_input.attachment"].sudo()

        payload = []
        for upload in files:
            upload.stream.seek(0, 2)
            size_mb = upload.stream.tell() / (1024 * 1024) if upload.stream else 0
            upload.stream.seek(0)
            if max_size_mb and size_mb > max_size_mb:
                return request.make_json_response(
                    {"error": "file_too_large", "limit": max_size_mb, "filename": upload.filename}, status=413
                )

            attachment = Attachment.create(
                {
                    "name": upload.filename,
                    "datas": base64.b64encode(upload.read()),
                    "res_model": "survey.user_input",
                    "res_id": answer.id,
                    "mimetype": upload.mimetype,
                }
            )
            link = Link.create(
                {
                    "user_input_id": answer.id,
                    "question_id": question.id,
                    "attachment_id": attachment.id,
                }
            )
            payload.append(
                {
                    "link_id": link.id,
                    "attachment_id": attachment.id,
                    "name": attachment.name,
                    "mimetype": attachment.mimetype,
                    "url": f"/web/content/{attachment.id}?download=1",
                }
            )

        return request.make_json_response({"attachments": payload})

    @http.route(
        "/survey_extension/attachment/remove",
        type="json",
        auth="public",
        website=True,
    )
    def remove_attachment(self, survey_token, answer_token, link_id):
        _survey, answer, error_response = self._can_handle_request(
            survey_token, answer_token, require_editable=True
        )
        if error_response:
            return error_response.json_body if hasattr(error_response, "json_body") else False

        try:
            link_id_int = int(link_id)
        except (TypeError, ValueError):
            return {"error": "invalid_link"}

        link = request.env["survey.user_input.attachment"].sudo().browse(link_id_int)
        if not link or not link.exists():
            return {"error": "not_found"}
        if link.user_input_id.id != answer.id:
            return {"error": "forbidden"}

        link.unlink()
        return {"result": True}
