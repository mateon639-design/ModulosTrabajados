/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

const SurveyFormWidget = publicWidget.registry.SurveyFormWidget;

const ERROR_MESSAGES = {
    invalid_question: _t('No se reconoció la pregunta objetivo.'),
    missing_file: _t('Selecciona un archivo para continuar.'),
    readonly: _t('La encuesta ya no permite cargar archivos.'),
    no_answer: _t('No se encontró una participación activa.'),
    forbidden: _t('No tienes permisos para modificar este archivo.'),
    not_found: _t('El archivo ya fue eliminado.'),
};

function buildAttachmentItem(data, readonly) {
    const $item = $('<div/>', {
        class: 'o_survey_attachment_item d-flex align-items-center gap-2',
        'data-link-id': data.link_id,
        'data-attachment-id': data.attachment_id,
    });
    const $link = $('<a/>', {
        class: 'o_survey_attachment_link',
        href: data.url,
        target: '_blank',
        rel: 'noopener',
        text: data.name,
    }).prepend($('<i/>', { class: 'fa fa-paperclip me-1' }));
    $item.append($link);
    if (data.mimetype) {
        $item.append($('<span/>', { class: 'text-muted small', text: data.mimetype }));
    }
    if (!readonly) {
        const $remove = $('<button/>', {
            type: 'button',
            class: 'btn btn-sm btn-link text-danger o_survey_attachment_remove',
            'data-link-id': data.link_id,
        }).append($('<i/>', { class: 'fa fa-times' }));
        $item.append($remove);
    }
    return $item;
}

function isReadonlyArea($area) {
    const value = $area.data('readonly');
    if (typeof value === 'boolean') {
        return value;
    }
    if (typeof value === 'string') {
        return value.toLowerCase() === 'true';
    }
    return false;
}

SurveyFormWidget.include({
    start() {
        return this._super.apply(this, arguments).then(() => {
            this._ensureAttachmentHandlers();
            this._initAttachmentAreas();
        });
    },

    _onNextScreenDone() {
        const result = this._super.apply(this, arguments);
        this._initAttachmentAreas();
        return result;
    },

    _ensureAttachmentHandlers() {
        if (this._attachmentHandlersBound) {
            return;
        }
        this._attachmentHandlersBound = true;
        this.$el.on('click', '.o_survey_attachment_add', this._onAttachmentAddClick.bind(this));
        this.$el.on('change', '.o_survey_attachment_input', this._onAttachmentInputChange.bind(this));
        this.$el.on('click', '.o_survey_attachment_remove', this._onAttachmentRemoveClick.bind(this));
    },

    _initAttachmentAreas() {
        this.$('.o_survey_attachment_area').each((_, element) => {
            const $area = $(element);
            const hasList = $area.find('.o_survey_attachment_list').length;
            if (!hasList) {
                $area.find('.o_survey_attachment_empty').toggleClass('d-none', false);
            } else {
                $area.find('.o_survey_attachment_empty').toggleClass('d-none', true);
            }
            if (isReadonlyArea($area)) {
                $area.addClass('o_survey_attachment_readonly');
            }
        });
    },

    _onAttachmentAddClick(event) {
        event.preventDefault();
        const $area = $(event.currentTarget).closest('.o_survey_attachment_area');
        if (isReadonlyArea($area)) {
            return;
        }
        const $input = $area.find('.o_survey_attachment_input');
        if ($input.length) {
            $input.trigger('click');
        }
    },

    async _onAttachmentInputChange(event) {
        const $input = $(event.currentTarget);
        const $area = $input.closest('.o_survey_attachment_area');
        const files = Array.from(event.currentTarget.files || []);
        if (!files.length) {
            return;
        }
        await this._uploadAttachments($area, files);
        $input.val('');
    },

    async _uploadAttachments($area, files) {
        const surveyToken = $area.data('surveyToken');
        const answerToken = $area.data('answerToken');
        const questionId = $area.data('questionId');
        const csrfToken = this.$('input[name="csrf_token"]').val();
        if (!(surveyToken && answerToken && questionId && csrfToken)) {
            this.displayNotification({
                title: _t('Error'),
                message: _t('No fue posible preparar el envío del archivo.'),
                type: 'danger',
            });
            return;
        }
        const formData = new FormData();
        formData.append('csrf_token', csrfToken);
        formData.append('survey_token', surveyToken);
        formData.append('answer_token', answerToken);
        formData.append('question_id', questionId);
        files.forEach((file) => formData.append('file', file));

        let response;
        try {
            response = await fetch('/survey_extension/attachment/upload', {
                method: 'POST',
                body: formData,
                credentials: 'include',
            });
        } catch (error) {
            this.displayNotification({
                title: _t('Error de red'),
                message: _t('No fue posible subir el archivo. Inténtalo nuevamente.'),
                type: 'danger',
            });
            return;
        }

        let payload;
        try {
            payload = await response.json();
        } catch (error) {
            this.displayNotification({
                title: _t('Error'),
                message: _t('Respuesta inesperada del servidor.'),
                type: 'danger',
            });
            return;
        }

        if (!response.ok || payload.error) {
            let message;
            if (payload && payload.error === 'file_too_large') {
                const limit = payload.limit ? `${payload.limit} MB` : '';
                message = limit ? _t('El archivo excede el tamaño permitido (%s).', limit) : _t('El archivo excede el tamaño permitido.');
            } else if (payload && payload.error) {
                message = ERROR_MESSAGES[payload.error] || payload.error;
            } else {
                message = _t('No se pudo guardar el archivo.');
            }
            this.displayNotification({
                title: _t('Error'),
                message,
                type: 'danger',
            });
            return;
        }

        const attachments = payload.attachments || [];
        attachments.forEach((attachment) => this._appendAttachment($area, attachment));
    },

    _appendAttachment($area, attachment) {
        let $list = $area.find('.o_survey_attachment_list');
    const readonly = isReadonlyArea($area);
        if (!$list.length) {
            $list = $('<div/>', {
                class: 'o_survey_attachment_list d-flex flex-column gap-2',
            });
            $area.prepend($list);
        }
        const $newItem = buildAttachmentItem(attachment, readonly);
        $list.append($newItem);
        $area.find('.o_survey_attachment_empty').addClass('d-none');
    },

    async _onAttachmentRemoveClick(event) {
        event.preventDefault();
        const $button = $(event.currentTarget);
        const $area = $button.closest('.o_survey_attachment_area');
        if (isReadonlyArea($area)) {
            return;
        }
        const linkId = $button.data('linkId');
        if (!linkId) {
            return;
        }
        $button.prop('disabled', true);
        let result;
        try {
            result = await rpc('/survey_extension/attachment/remove', {
                survey_token: $area.data('surveyToken'),
                answer_token: $area.data('answerToken'),
                link_id: linkId,
            });
        } catch (error) {
            this.displayNotification({
                title: _t('Error de red'),
                message: _t('No fue posible eliminar el archivo.'),
                type: 'danger',
            });
            $button.prop('disabled', false);
            return;
        }

        $button.prop('disabled', false);
        if (result && result.error) {
            this.displayNotification({
                title: _t('Error'),
                message: ERROR_MESSAGES[result.error] || result.error,
                type: 'danger',
            });
            return;
        }

        const $list = $area.find('.o_survey_attachment_list');
        $area
            .find(`.o_survey_attachment_item[data-link-id="${linkId}"]`)
            .remove();
        if (!$list.children().length) {
            $list.remove();
            $area.find('.o_survey_attachment_empty').removeClass('d-none');
        }
    },
});
