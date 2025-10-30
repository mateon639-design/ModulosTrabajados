/** @odoo-module **/
/**
 * Archivo: survey_wpm_questions.js
 * Propósito: Lógica JavaScript para preguntas de tipo WPM (Palabras Por Minuto)
 * 
 * Este archivo maneja:
 * 1. Temporizador para medir tiempo de lectura/escritura
 * 2. Cálculo en tiempo real de WPM
 * 3. Clasificación de velocidad (lento/promedio/rápido)
 * 4. Validación de límites de tiempo
 * 5. Prevención de copiar/pegar en modo escritura
 */

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

// ============================================================================
// WIDGET: Pregunta WPM de Lectura
// ============================================================================

publicWidget.registry.SurveyWPMReading = publicWidget.Widget.extend({
    selector: '.o_survey_question_wpm_reading',
    events: {
        'click .o_wpm_start_btn': '_onStartReading',
        'click .o_wpm_finish_btn': '_onFinishReading',
    },

    /**
     * Inicialización del widget
     */
    start: function () {
        this._super.apply(this, arguments);
        
        // Datos de la pregunta
        this.questionId = this.$el.data('question-id');
        this.wordCount = this.$el.data('word-count') || 0;
        this.showTimer = this.$el.data('show-timer');
        this.minTime = this.$el.data('min-time') || 0;
        this.maxTime = this.$el.data('max-time') || 0;
        
        // Estado del temporizador
        this.startTime = null;
        this.endTime = null;
        this.timerInterval = null;
        this.elapsedSeconds = 0;
        
        // Referencias a elementos
        this.$startScreen = this.$('.o_wpm_start_screen');
        this.$readingScreen = this.$('.o_wpm_reading_screen');
        this.$resultScreen = this.$('.o_wpm_result_screen');
        this.$timerDisplay = this.$('.o_wpm_timer_display');
        this.$currentWPM = this.$('.o_wpm_current_wpm');
        
        return this._super.apply(this, arguments);
    },

    /**
     * Limpiar al destruir
     */
    destroy: function () {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        this._super.apply(this, arguments);
    },

    /**
     * Evento: Comenzar lectura
     */
    _onStartReading: function (ev) {
        ev.preventDefault();
        
        // Registrar tiempo de inicio
        this.startTime = new Date();
        this.elapsedSeconds = 0;
        
        // Cambiar interfaz
        this.$startScreen.hide();
        this.$readingScreen.show();
        
        // Iniciar temporizador
        this._startTimer();
        
        // Guardar timestamp
        this.$('.o_wpm_start_timestamp').val(this.startTime.toISOString());
    },

    /**
     * Evento: Finalizar lectura
     */
    _onFinishReading: function (ev) {
        ev.preventDefault();
        
        // Registrar tiempo de fin
        this.endTime = new Date();
        
        // Detener temporizador
        this._stopTimer();
        
        // Calcular resultados
        const timeInSeconds = (this.endTime - this.startTime) / 1000;
        const wpm = this._calculateWPM(this.wordCount, timeInSeconds);
        const classification = this._classifyWPM(wpm);
        
        // Validar límites de tiempo
        if (this.minTime > 0 && timeInSeconds < this.minTime) {
            this._showWarning(_t('Advertencia: El tiempo es muy corto. ¿Realmente leíste todo el texto?'));
        }
        
        if (this.maxTime > 0 && timeInSeconds > this.maxTime) {
            this._showWarning(_t('Has excedido el tiempo máximo permitido.'));
        }
        
        // Guardar datos en campos ocultos
        this.$('.o_wpm_completed').val('1');  // Marcar como completada
        this.$('.o_wpm_time_input').val(timeInSeconds.toFixed(2));
        this.$('.o_wpm_word_count_input').val(this.wordCount);
        this.$('.o_wpm_score_input').val(wpm.toFixed(2));
        this.$('.o_wpm_end_timestamp').val(this.endTime.toISOString());
        
        // Mostrar resultados
        this._showResults(wpm, timeInSeconds, classification);
    },

    /**
     * Inicia el temporizador
     */
    _startTimer: function () {
        const self = this;
        
        this.timerInterval = setInterval(function () {
            self.elapsedSeconds++;
            
            // Actualizar display del temporizador
            if (self.showTimer) {
                self.$timerDisplay.text(self._formatTime(self.elapsedSeconds));
            }
            
            // Actualizar WPM en tiempo real
            const currentWPM = self._calculateWPM(self.wordCount, self.elapsedSeconds);
            self.$currentWPM.text(currentWPM.toFixed(0));
        }, 1000);
    },

    /**
     * Detiene el temporizador
     */
    _stopTimer: function () {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    },

    /**
     * Calcula WPM (Palabras Por Minuto)
     * Formula: WPM = (palabras / segundos) * 60
     */
    _calculateWPM: function (words, seconds) {
        if (seconds === 0) return 0;
        return (words / seconds) * 60;
    },

    /**
     * Formatea segundos a MM:SS
     */
    _formatTime: function (totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
    },

    /**
     * Clasifica WPM según velocidad
     */
    _classifyWPM: function (wpm) {
        // Umbrales predeterminados (se pueden personalizar desde Python)
        if (wpm < 150) return { label: 'Lento', class: 'bg-danger' };
        if (wpm < 250) return { label: 'Promedio', class: 'bg-warning' };
        if (wpm < 350) return { label: 'Rápido', class: 'bg-success' };
        return { label: 'Excepcional', class: 'bg-primary' };
    },

    /**
     * Muestra los resultados finales
     */
    _showResults: function (wpm, timeInSeconds, classification) {
        // Ocultar pantalla de lectura
        this.$readingScreen.hide();
        
        // Actualizar datos del resultado
        this.$('.o_wpm_final_score').text(wpm.toFixed(0));
        this.$('.o_wpm_final_time').text(this._formatTime(Math.round(timeInSeconds)));
        this.$('.o_wpm_classification_badge')
            .text(classification.label)
            .removeClass('bg-danger bg-warning bg-success bg-primary')
            .addClass(classification.class);
        
        // Mostrar pantalla de resultado
        this.$resultScreen.fadeIn();
    },

    /**
     * Muestra advertencia
     */
    _showWarning: function (message) {
        // Crear alerta temporal
        const $warning = $('<div class="alert alert-warning alert-dismissible fade show" role="alert">')
            .html('<i class="fa fa-exclamation-triangle me-2"></i>' + message +
                  '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>');
        
        this.$readingScreen.prepend($warning);
        
        // Auto-ocultar después de 5 segundos
        setTimeout(function () {
            $warning.fadeOut(function () { $(this).remove(); });
        }, 5000);
    },
});

// ============================================================================
// WIDGET: Pregunta WPM de Escritura
// ============================================================================

publicWidget.registry.SurveyWPMTyping = publicWidget.Widget.extend({
    selector: '.o_survey_question_wpm_typing',
    events: {
        'input .o_wpm_typing_area': '_onTyping',
        'paste .o_wpm_typing_area': '_onPaste',
        'click .o_wpm_typing_finish_btn': '_onFinishTyping',
    },

    /**
     * Inicialización
     */
    start: function () {
        this._super.apply(this, arguments);
        
        // Datos de la pregunta
        this.questionId = this.$el.data('question-id');
        this.showTimer = this.$el.data('show-timer');
        this.allowPaste = this.$el.data('allow-paste');
        this.minTime = this.$el.data('min-time') || 0;
        this.maxTime = this.$el.data('max-time') || 0;
        
        // Estado
        this.startTime = null;
        this.endTime = null;
        this.timerInterval = null;
        this.elapsedSeconds = 0;
        this.hasStarted = false;
        
        // Referencias
        this.$textarea = this.$('.o_wpm_typing_area');
        this.$finishBtn = this.$('.o_wpm_typing_finish_btn');
        this.$resultScreen = this.$('.o_wpm_result_screen');
        this.$wordCountDisplay = this.$('.o_wpm_word_count_display');
        this.$charCountDisplay = this.$('.o_wpm_char_count_display');
        this.$timerDisplay = this.$('.o_wpm_timer_display');
        this.$currentWPM = this.$('.o_wpm_current_wpm');
        
        return this._super.apply(this, arguments);
    },

    /**
     * Limpiar
     */
    destroy: function () {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        this._super.apply(this, arguments);
    },

    /**
     * Evento: Usuario está escribiendo
     */
    _onTyping: function (ev) {
        const text = this.$textarea.val();
        
        // Si es la primera vez que escribe, iniciar temporizador
        if (!this.hasStarted && text.trim().length > 0) {
            this._startTyping();
        }
        
        // Actualizar contadores en tiempo real
        this._updateCounters(text);
    },

    /**
     * Evento: Intento de pegar texto
     */
    _onPaste: function (ev) {
        if (!this.allowPaste) {
            ev.preventDefault();
            this._showWarning(_t('Copiar y pegar no está permitido en esta pregunta.'));
            return false;
        }
    },

    /**
     * Evento: Finalizar escritura
     */
    _onFinishTyping: function (ev) {
        ev.preventDefault();
        
        const text = this.$textarea.val().trim();
        
        if (text.length === 0) {
            this._showWarning(_t('Debes escribir al menos una palabra antes de finalizar.'));
            return;
        }
        
        // Registrar tiempo de fin
        this.endTime = new Date();
        
        // Detener temporizador
        this._stopTimer();
        
        // Contar palabras
        const wordCount = this._countWords(text);
        const timeInSeconds = (this.endTime - this.startTime) / 1000;
        const wpm = this._calculateWPM(wordCount, timeInSeconds);
        const classification = this._classifyWPM(wpm);
        
        // Validar límites
        if (this.minTime > 0 && timeInSeconds < this.minTime) {
            this._showWarning(_t('Advertencia: El tiempo es muy corto.'));
        }
        
        if (this.maxTime > 0 && timeInSeconds > this.maxTime) {
            this._showWarning(_t('Has excedido el tiempo máximo permitido.'));
        }
        
        // Guardar datos
        this.$('.o_wpm_completed').val('1');  // Marcar como completada
        this.$('.o_wpm_time_input').val(timeInSeconds.toFixed(2));
        this.$('.o_wpm_word_count_input').val(wordCount);
        this.$('.o_wpm_score_input').val(wpm.toFixed(2));
        this.$('.o_wpm_end_timestamp').val(this.endTime.toISOString());
        
        // Deshabilitar textarea
        this.$textarea.prop('disabled', true);
        this.$finishBtn.prop('disabled', true);
        
        // Mostrar resultados
        this._showResults(wpm, wordCount, classification);
    },

    /**
     * Inicia el temporizador de escritura
     */
    _startTyping: function () {
        this.hasStarted = true;
        this.startTime = new Date();
        this.elapsedSeconds = 0;
        
        // Habilitar botón de finalizar
        this.$finishBtn.prop('disabled', false);
        
        // Guardar timestamp de inicio
        this.$('.o_wpm_start_timestamp').val(this.startTime.toISOString());
        
        // Iniciar temporizador
        const self = this;
        this.timerInterval = setInterval(function () {
            self.elapsedSeconds++;
            
            if (self.showTimer) {
                self.$timerDisplay.text(self._formatTime(self.elapsedSeconds));
            }
            
            // Actualizar WPM en tiempo real
            const text = self.$textarea.val();
            const wordCount = self._countWords(text);
            const currentWPM = self._calculateWPM(wordCount, self.elapsedSeconds);
            self.$currentWPM.text(currentWPM.toFixed(0));
        }, 1000);
    },

    /**
     * Detiene el temporizador
     */
    _stopTimer: function () {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    },

    /**
     * Actualiza contadores de palabras y caracteres
     */
    _updateCounters: function (text) {
        const wordCount = this._countWords(text);
        const charCount = text.length;
        
        this.$wordCountDisplay.text(wordCount);
        this.$charCountDisplay.text(charCount);
    },

    /**
     * Cuenta palabras en un texto
     */
    _countWords: function (text) {
        if (!text || text.trim().length === 0) return 0;
        
        // Usar regex para contar palabras (similar a Python)
        const words = text.trim().match(/\b\w+\b/g);
        return words ? words.length : 0;
    },

    /**
     * Calcula WPM
     */
    _calculateWPM: function (words, seconds) {
        if (seconds === 0) return 0;
        return (words / seconds) * 60;
    },

    /**
     * Formatea tiempo
     */
    _formatTime: function (totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
    },

    /**
     * Clasifica WPM
     */
    _classifyWPM: function (wpm) {
        if (wpm < 150) return { label: 'Lento', class: 'bg-danger' };
        if (wpm < 250) return { label: 'Promedio', class: 'bg-warning' };
        if (wpm < 350) return { label: 'Rápido', class: 'bg-success' };
        return { label: 'Excepcional', class: 'bg-primary' };
    },

    /**
     * Muestra resultados
     */
    _showResults: function (wpm, wordCount, classification) {
        this.$('.o_wpm_final_score').text(wpm.toFixed(0));
        this.$('.o_wpm_final_words').text(wordCount);
        this.$('.o_wpm_classification_badge')
            .text(classification.label)
            .removeClass('bg-danger bg-warning bg-success bg-primary')
            .addClass(classification.class);
        
        this.$resultScreen.fadeIn();
    },

    /**
     * Muestra advertencia
     */
    _showWarning: function (message) {
        const $warning = $('<div class="alert alert-warning alert-dismissible fade show" role="alert">')
            .html('<i class="fa fa-exclamation-triangle me-2"></i>' + message +
                  '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>');
        
        this.$textarea.before($warning);
        
        setTimeout(function () {
            $warning.fadeOut(function () { $(this).remove(); });
        }, 5000);
    },
});

// Registrar extensión del SurveyFormWidget para procesar datos WPM
const SurveyFormWidget = publicWidget.registry.SurveyFormWidget;

if (SurveyFormWidget) {
    SurveyFormWidget.include({
        /**
         * Validación antes de enviar el formulario
         */
        _prepareSubmitValues: function (formData, params) {
            const result = this._super.apply(this, arguments);
            
            // Validar que las preguntas WPM estén completadas
            this.$('.o_survey_question_wpm_reading, .o_survey_question_wpm_typing').each(function () {
                const $question = $(this);
                const timeInput = $question.find('.o_wpm_time_input').val();
                
                if (!timeInput || parseFloat(timeInput) === 0) {
                    // Marcar como inválida si no se completó
                    $question.addClass('o_survey_question_error');
                }
            });
            
            return result;
        },
    });
}
