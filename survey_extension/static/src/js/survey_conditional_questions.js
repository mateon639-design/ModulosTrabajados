/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SurveyConditionalQuestions = publicWidget.Widget.extend({
    selector: ".o_survey_form",

    events: {
        "change input[type='radio']": "_onAnswerChange",
        "change select": "_onAnswerChange",
        "change input[type='checkbox']": "_onAnswerChange",
    },

    start() {
        this._super(...arguments);
        this._initConditionalQuestions();
        this._checkAllConditions();
    },

    // Indexa preguntas condicionales y las oculta inicialmente
    _initConditionalQuestions() {
        this.conditionalQuestions = {};
        const $questions = this.$(".js_question-wrapper[data-conditional='true']");
        $questions.each((_, el) => {
            const $q = $(el);
            const qId = $q.data("question-id");
            const parentQ = $q.data("conditional-question-id");
            const triggerA = $q.data("conditional-answer-id");
            if (qId && parentQ && triggerA) {
                this.conditionalQuestions[qId] = {
                    element: $q,
                    dependsOn: String(parentQ),
                    requiredAnswer: String(triggerA),
                };
                $q.hide();
                this._toggleRequired($q, false);
                this._clearAnswer($q);
            }
        });
    },

    // Estado inicial (útil al volver atrás o recargar una página del wizard)
    _checkAllConditions() {
        Object.values(this.conditionalQuestions).forEach((cfg) => {
            this._checkConditionsForQuestion(cfg.dependsOn);
        });
    },

    _onAnswerChange(ev) {
        const $input = $(ev.currentTarget);
        const $wrapper = $input.closest(".js_question-wrapper,[data-question-id]");
        const qId = $wrapper.data("question-id");
        if (qId != null) {
            this._checkConditionsForQuestion(String(qId));
        }
    },

    // Muestra/oculta las preguntas que dependen de una pregunta dada
    _checkConditionsForQuestion(questionId) {
        Object.entries(this.conditionalQuestions).forEach(([childId, cfg]) => {
            if (cfg.dependsOn === String(questionId)) {
                const selected = this._getSelectedAnswer(questionId);
                if (selected != null && String(selected) === cfg.requiredAnswer) {
                    if (cfg.element.is(":hidden")) {
                        cfg.element.stop(true, true).slideDown(200);
                    }
                    this._toggleRequired(cfg.element, true);
                } else {
                    if (cfg.element.is(":visible")) {
                        cfg.element.stop(true, true).slideUp(200);
                    }
                    this._clearAnswer(cfg.element);
                    this._toggleRequired(cfg.element, false);
                }
            }
        });
    },

    // Detecta la respuesta actual de una pregunta (radio / select / checkbox)
    _getSelectedAnswer(questionId) {
        const $q = this.$(`.js_question-wrapper[data-question-id='${questionId}']`);
        if (!$q.length) return null;

        // Radio (opción única)
        const $r = $q.find("input[type='radio']:checked");
        if ($r.length) return $r.data("answer-id") ?? $r.val();

        // Select
        const $s = $q.find("select");
        if ($s.length) {
            const $opt = $s.find("option:selected");
            return $opt.data("answer-id") ?? $opt.val();
        }

        // Checkbox (múltiple): tomamos el primero marcado (gatillo binario típico)
        const $c = $q.find("input[type='checkbox']:checked");
        if ($c.length) return $c.first().data("answer-id") ?? $c.first().val();

        return null;
        // Nota: para matrices u otros tipos, se podría ampliar aquí.
    },

    // Limpia respuesta al ocultar (para evitar envíos no deseados)
    _clearAnswer($q) {
        $q.find("input[type='radio'], input[type='checkbox']").prop("checked", false);
        $q.find("select").val("");
        $q.find("input[type='text'], textarea, input[type='number'], input[type='email']").val("");
    },

    // Activa/desactiva required respetando el estado original
    _toggleRequired($q, makeRequired) {
        const originally = Boolean($q.data("originally-required"));
        const $inputs = $q.find("input, select, textarea");
        const $label = $q.find(".js_question_label");

        if (makeRequired && originally) {
            // Evitar required en inputs ocultos (HTML5 valida incluso si display:none)
            $inputs.each((_, el) => {
                const $el = $(el);
                if ($el.is(":visible")) $el.prop("required", true);
            });
            $label.addClass("o_survey_required");
        } else {
            $inputs.prop("required", false);
            $label.removeClass("o_survey_required");
        }
    },
});

export default publicWidget.registry.SurveyConditionalQuestions;
