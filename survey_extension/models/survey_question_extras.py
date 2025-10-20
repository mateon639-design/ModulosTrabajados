# -*- coding: utf-8 -*-
"""
Archivo: survey_question_extras.py
Propósito: Añade funcionalidades extra a las preguntas de encuestas

Este archivo extiende las preguntas de Odoo con nuevas características:
1. Categorización de preguntas
2. Peso/importancia de preguntas
3. Marcado de preguntas clave
4. Visibilidad condicional (mostrar preguntas solo si se cumple una condición)
"""

from odoo import fields, models, api


# ============================================================================
# MODELO: Categoría de Pregunta
# ============================================================================
class SurveyQuestionCategory(models.Model):
    """
    Modelo para clasificar preguntas en categorías
    
    ¿Para qué sirve?
    ----------------
    Permite organizar las preguntas en grupos como:
    - Preguntas técnicas
    - Preguntas de actitud
    - Preguntas generales
    - etc.
    
    Esto ayuda a:
    - Organizar mejor las encuestas
    - Generar reportes por categoría
    - Filtrar preguntas fácilmente
    """
    
    # Nombre técnico del modelo en Odoo (así se identifica en la base de datos)
    _name = "survey.question.category"
    
    # Descripción legible del modelo
    _description = "Categoría de pregunta de encuesta"
    
    # Campo por el cual se ordenarán los registros (alfabéticamente por nombre)
    _order = "name"

    # CAMPOS DEL MODELO
    # -----------------
    
    # Nombre de la categoría (obligatorio)
    # Ejemplo: "Preguntas Técnicas", "Preguntas de Satisfacción"
    name = fields.Char(
        string="Nombre",           # Etiqueta que verá el usuario
        required=True              # No se puede guardar sin un nombre
    )
    
    # Descripción detallada de para qué sirve esta categoría (opcional)
    description = fields.Text(string="Descripción")
    
    # Si la categoría está activa o archivada
    # True = se puede usar, False = está archivada (no se muestra en listas)
    active = fields.Boolean(default=True)


# ============================================================================
# EXTENSIÓN: Pregunta de Encuesta
# ============================================================================
class SurveyQuestion(models.Model):
    """
    Extensión del modelo de preguntas de encuestas de Odoo
    
    ¿Qué hace _inherit?
    -------------------
    No creamos un modelo nuevo, sino que EXTENDEMOS uno existente.
    Es como agregarle nuevas características a algo que ya existe.
    
    El modelo "survey.question" ya existe en Odoo (viene del módulo survey).
    Nosotros le añadimos más campos y funcionalidades.
    """
    
    # Indicamos que estamos extendiendo el modelo de preguntas existente
    _inherit = "survey.question"

    # CAMPOS NUEVOS QUE AÑADIMOS
    # --------------------------
    
    # 1. PESO DE LA PREGUNTA
    # ----------------------
    # Indica qué tan importante es esta pregunta al calcular la nota final
    weight = fields.Float(
        string="Peso de la pregunta",
        default=1.0,  # Por defecto, todas las preguntas valen lo mismo
        help="Importancia relativa. 2.0 equivale al doble que 1.0."
        # Ejemplo: Si una pregunta tiene peso 2.0 y otra peso 1.0,
        #          la primera vale el doble al calcular la calificación
    )
    
    # 2. CATEGORÍA DE LA PREGUNTA
    # ---------------------------
    # Permite clasificar la pregunta en una categoría
    category_id = fields.Many2one(
        "survey.question.category",  # Relaciona con el modelo de categorías
        string="Categoría",
        help="Clasifica la pregunta (p. ej.: Técnica, Actitudinal, General)."
        # Many2one = "muchos a uno"
        # Significa: Muchas preguntas pueden tener la misma categoría
    )
    
    # 3. PREGUNTA CLAVE
    # -----------------
    # Marca si esta pregunta es especialmente importante
    is_key = fields.Boolean(
        string="¿Es pregunta clave?",
        help="Marca si esta pregunta es clave dentro de la encuesta."
        # Útil para:
        # - Filtrar preguntas importantes en reportes
        # - Contar cuántas preguntas clave tiene una encuesta
        # - Dar más visibilidad a preguntas críticas
    )
    
    # ========================================================================
    # CAMPOS PARA VISIBILIDAD CONDICIONAL
    # ========================================================================
    # Estos campos permiten mostrar/ocultar preguntas según las respuestas
    # a preguntas anteriores
    
    # 4. ACTIVAR CONDICIÓN
    # --------------------
    # Indica si esta pregunta se mostrará solo bajo ciertas condiciones
    is_conditional = fields.Boolean(
        string="Pregunta condicional",
        default=False,  # Por defecto, las preguntas se muestran siempre
        help="Activa si esta pregunta debe aparecer solo cuando se cumple una condición específica."
        # Ejemplo de uso:
        # Pregunta 1: "¿Tus datos son correctos?" (Sí/No)
        # Pregunta 2: "Corrige tus datos" (solo se muestra si la respuesta es "No")
    )
    
    # 5. PREGUNTA DE LA QUE DEPENDE
    # ------------------------------
    # Selecciona QUÉ pregunta anterior determina si se muestra esta o no
    conditional_question_id = fields.Many2one(
        "survey.question",  # Relaciona con otra pregunta de la misma encuesta
        string="Pregunta que determina la visibilidad",
        help="Selecciona la pregunta cuya respuesta determinará si esta pregunta se muestra o no."
        # Ejemplo: Si seleccionamos "¿Tus datos son correctos?",
        #          esta pregunta dependerá de la respuesta a esa pregunta
    )
    
    # 6. RESPUESTA QUE ACTIVA ESTA PREGUNTA
    # --------------------------------------
    # Selecciona QUÉ respuesta específica debe darse para mostrar esta pregunta
    conditional_answer_id = fields.Many2one(
        "survey.question.answer",  # Relaciona con una respuesta específica
        string="Respuesta que activa esta pregunta",
        domain="[('question_id', '=', conditional_question_id)]",
        # El domain es un filtro que dice:
        # "Solo muestra respuestas que pertenezcan a la pregunta seleccionada arriba"
        help="Selecciona la respuesta específica que debe elegirse para que esta pregunta se muestre."
        # Ejemplo: Si la pregunta es "¿Tus datos son correctos?",
        #          seleccionaríamos la respuesta "No"
    )
    
    # ========================================================================
    # MÉTODOS (FUNCIONES)
    # ========================================================================
    
    @api.onchange('is_conditional')
    def _onchange_is_conditional(self):
        """
        Se ejecuta cuando el usuario cambia el checkbox "Pregunta condicional"
        
        ¿Qué hace?
        ----------
        Si el usuario desactiva la opción "Pregunta condicional",
        automáticamente limpia los campos relacionados (pregunta y respuesta).
        
        ¿Por qué?
        ---------
        Para evitar que queden datos inconsistentes. Si ya no es condicional,
        no tiene sentido que tenga una pregunta y respuesta asociada.
        
        Es como cuando desactivas "Enviar por correo" en un formulario,
        automáticamente se borra el campo de email porque ya no lo necesitas.
        """
        if not self.is_conditional:
            # Limpiar los campos condicionales
            self.conditional_question_id = False
            self.conditional_answer_id = False


