# -*- coding: utf-8 -*-
{
    # Información básica
    "name": "Survey Extension",
    "summary": "Extiende Encuestas con público objetivo, ranking y dashboards.",
    "version": "1.4.0",
    "category": "Surveys",
    "author": "Your Company",
    "website": "https://www.example.com",

    # Dependencias (módulos requeridos)
    "depends": ["base", "survey"],

    # Archivos de datos y vistas
    "data": [
        "security/ir.model.access.csv",
        "data/audience_categories.xml",
        "data/question_categories.xml",
        "data/survey_sequence.xml",
        "data/survey_trash_cron.xml",
    "views/survey_extension_menu.xml",
    "views/survey_user_input_inherit_views.xml",
    "views/survey_survey_inherit_views.xml",
    "views/survey_ranking_dashboard_views.xml",
    "views/report_survey_summary.xml",
        "views/survey_edit_question_title_wizard_views.xml",
        "views/survey_version_wizard_views.xml",
        "views/survey_code_selection_wizard_views.xml",
        "views/survey_trash_views.xml",
        "views/survey_key_counter_views.xml",
        "views/survey_templates.xml",
        "views/survey_scoring_templates.xml",
        "views/survey_calificacion_average_views.xml",
    ],

    # Archivos estáticos (frontend)
    "assets": {
        "survey.survey_assets": [
            "survey_extension/static/src/js/survey_conditional_questions.js",
            "survey_extension/static/src/js/survey_answer_attachments.js",
            "survey_extension/static/src/scss/survey_extension.scss",
        ],
        "web.assets_frontend": [],
        "web.assets_backend": [
            "survey_extension/static/src/scss/survey_ranking_dashboard.scss",
        ],
        "web.assets_tests": [],
    },

    # Configuración
    "application": False,
    "installable": True,
    "license": "LGPL-3",

    # Hooks
    "pre_init_hook": "migrate_version_year_to_char",
    "post_init_hook": "post_init_hook",
}
