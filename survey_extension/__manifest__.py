# -*- coding: utf-8 -*-
{
    # Información básica
    "name": "Survey Extension",
    "summary": "Extiende Encuestas con público objetivo administrable.",
    "version": "1.0.1",
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
        "views/survey_extension_menu.xml",
        "views/survey_user_input_inherit_views.xml",
        "views/report_survey_summary.xml",
        "views/survey_survey_inherit_views.xml",
        "views/survey_key_counter_views.xml",
        "views/survey_templates.xml",
        "views/survey_scoring_templates.xml",
        "views/survey_calificacion_average_views.xml",
    ],

    # Archivos estáticos (frontend)
    "assets": {
        "web.assets_frontend": [
            "survey_extension/static/src/js/survey_conditional_questions.js",
        ],
        "web.assets_backend": [],
        "web.assets_tests": [],
    },

    # Configuración
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
