# -*- coding: utf-8 -*-
{
    "name": "Survey Extension",
    "summary": "Extiende Encuestas con Público objetivo administrable.",
    "version": "1.0.0",
    "category": "Surveys",
    "author": "Your Company",
    "website": "https://www.example.com",
    "depends": ["base", "survey"],
    "data": [
        "security/ir.model.access.csv",  # solo encabezado
        "data/audience_categories.xml",
        "data/question_categories.xml",
        "views/survey_user_input_inherit_views.xml",
        "views/survey_survey_inherit_views.xml",
        "views/survey_question_inherit_views.xml",
        "views/survey_key_counter_views.xml",
        "views/survey_templates.xml",
        "views/survey_scoring_templates.xml",
        "views/survey_calificacion_average_views.xml",
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_tests": []
    },
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
