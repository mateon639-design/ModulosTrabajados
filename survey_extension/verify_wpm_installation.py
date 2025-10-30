# -*- coding: utf-8 -*-
"""
Script de Verificación del Módulo WPM

Este script verifica que el módulo WPM esté correctamente instalado
y funcionando en Odoo 18.

Uso:
    python verify_wpm_installation.py

O desde la consola de Odoo:
    >>> exec(open('c:/ModulosOdoo18/survey_extension/verify_wpm_installation.py').read())
    >>> verify_wpm_installation(env)
"""

def verify_wpm_installation(env):
    """
    Verifica la instalación del módulo WPM
    
    Args:
        env: Entorno de Odoo (environment)
    """
    print("\n" + "="*80)
    print("VERIFICACIÓN DE INSTALACIÓN - MÓDULO WPM (Palabras Por Minuto)")
    print("="*80 + "\n")
    
    errors = []
    warnings = []
    success = []
    
    # ========================================================================
    # 1. Verificar que el modelo survey.question existe y tiene los campos WPM
    # ========================================================================
    print("1️⃣  Verificando modelo survey.question...")
    try:
        SurveyQuestion = env['survey.question']
        fields_dict = SurveyQuestion.fields_get()
        
        # Campos WPM esperados
        wpm_fields = [
            'wpm_reading_text',
            'wpm_word_count',
            'wpm_mode',
            'wpm_min_time',
            'wpm_max_time',
            'wpm_instructions',
            'wpm_show_timer',
            'wpm_allow_paste',
            'wpm_slow_threshold',
            'wpm_average_threshold',
            'wpm_fast_threshold',
        ]
        
        missing_fields = []
        for field in wpm_fields:
            if field not in fields_dict:
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Faltan campos en survey.question: {', '.join(missing_fields)}")
            print(f"   ❌ Faltan campos: {', '.join(missing_fields)}")
        else:
            success.append("Todos los campos WPM en survey.question están presentes")
            print(f"   ✅ Todos los campos WPM presentes ({len(wpm_fields)} campos)")
        
        # Verificar selection_add de question_type
        question_type_field = fields_dict.get('question_type', {})
        selection = question_type_field.get('selection', [])
        
        wpm_types = [item[0] for item in selection if item[0] in ('wpm_reading', 'wpm_typing')]
        
        if len(wpm_types) == 2:
            success.append("Tipos de pregunta WPM registrados correctamente")
            print(f"   ✅ Tipos WPM registrados: wpm_reading, wpm_typing")
        else:
            errors.append("No se encontraron los tipos de pregunta WPM en question_type")
            print(f"   ❌ Tipos WPM no encontrados en selection")
            
    except Exception as e:
        errors.append(f"Error al verificar survey.question: {str(e)}")
        print(f"   ❌ Error: {str(e)}")
    
    # ========================================================================
    # 2. Verificar modelo survey.user_input.line
    # ========================================================================
    print("\n2️⃣  Verificando modelo survey.user_input.line...")
    try:
        UserInputLine = env['survey.user_input.line']
        fields_dict = UserInputLine.fields_get()
        
        wpm_line_fields = [
            'wpm_time_seconds',
            'wpm_word_count',
            'wpm_score',
            'wpm_classification',
            'wpm_typed_text',
            'wpm_start_time',
            'wpm_end_time',
        ]
        
        missing_fields = []
        for field in wpm_line_fields:
            if field not in fields_dict:
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Faltan campos en survey.user_input.line: {', '.join(missing_fields)}")
            print(f"   ❌ Faltan campos: {', '.join(missing_fields)}")
        else:
            success.append("Todos los campos WPM en survey.user_input.line están presentes")
            print(f"   ✅ Todos los campos WPM presentes ({len(wpm_line_fields)} campos)")
            
    except Exception as e:
        errors.append(f"Error al verificar survey.user_input.line: {str(e)}")
        print(f"   ❌ Error: {str(e)}")
    
    # ========================================================================
    # 3. Verificar vistas XML
    # ========================================================================
    print("\n3️⃣  Verificando vistas XML...")
    try:
        IrUiView = env['ir.ui.view']
        
        # Buscar vistas WPM
        wpm_views = [
            'survey_extension.survey_question_form_inherit_wpm',
            'survey_extension.survey_user_input_line_tree_inherit_wpm',
            'survey_extension.survey_user_input_line_form_inherit_wpm',
            'survey_extension.survey_question_wpm_reading',
            'survey_extension.survey_question_wpm_typing',
        ]
        
        found_views = []
        missing_views = []
        
        for view_xml_id in wpm_views:
            try:
                view = env.ref(view_xml_id)
                found_views.append(view_xml_id)
            except:
                missing_views.append(view_xml_id)
        
        if missing_views:
            warnings.append(f"Algunas vistas WPM no se encontraron: {', '.join(missing_views)}")
            print(f"   ⚠️  Vistas no encontradas: {len(missing_views)}")
            for view in missing_views:
                print(f"       - {view}")
        
        if found_views:
            success.append(f"Vistas WPM encontradas: {len(found_views)}")
            print(f"   ✅ Vistas encontradas: {len(found_views)}/{len(wpm_views)}")
            
    except Exception as e:
        warnings.append(f"Error al verificar vistas: {str(e)}")
        print(f"   ⚠️  Error: {str(e)}")
    
    # ========================================================================
    # 4. Verificar archivos JavaScript
    # ========================================================================
    print("\n4️⃣  Verificando archivos JavaScript...")
    import os
    
    js_file = 'c:/ModulosOdoo18/survey_extension/static/src/js/survey_wpm_questions.js'
    
    if os.path.exists(js_file):
        success.append("Archivo JavaScript WPM encontrado")
        print(f"   ✅ survey_wpm_questions.js existe")
        
        # Verificar tamaño
        size = os.path.getsize(js_file)
        print(f"      Tamaño: {size:,} bytes")
        
        if size < 1000:
            warnings.append("El archivo JavaScript parece muy pequeño")
            print(f"      ⚠️  El archivo parece incompleto")
    else:
        errors.append("Archivo JavaScript WPM no encontrado")
        print(f"   ❌ survey_wpm_questions.js NO existe")
    
    # ========================================================================
    # 5. Crear pregunta de prueba
    # ========================================================================
    print("\n5️⃣  Creando pregunta de prueba...")
    try:
        # Buscar o crear encuesta de prueba
        Survey = env['survey.survey']
        test_survey = Survey.search([('title', '=', 'TEST WPM - Verificación')], limit=1)
        
        if not test_survey:
            test_survey = Survey.create({
                'title': 'TEST WPM - Verificación',
                'description': 'Encuesta de prueba para verificar módulo WPM',
                'access_mode': 'public',
            })
            print(f"   ℹ️  Encuesta de prueba creada: ID {test_survey.id}")
        else:
            print(f"   ℹ️  Usando encuesta existente: ID {test_survey.id}")
        
        # Crear pregunta WPM de lectura
        SurveyQuestion = env['survey.question']
        
        # Eliminar preguntas de prueba anteriores
        old_questions = SurveyQuestion.search([
            ('survey_id', '=', test_survey.id),
            ('title', 'ilike', 'TEST WPM')
        ])
        if old_questions:
            old_questions.unlink()
        
        reading_question = SurveyQuestion.create({
            'survey_id': test_survey.id,
            'title': 'TEST WPM - Velocidad de Lectura',
            'question_type': 'wpm_reading',
            'wpm_reading_text': 'Este es un texto de prueba para medir la velocidad de lectura. '
                               'Contiene varias palabras que el sistema contará automáticamente. '
                               'El usuario debe leer este texto y marcar cuando haya terminado.',
            'wpm_mode': 'reading',
            'wpm_show_timer': True,
            'wpm_instructions': 'Lee el texto completo y presiona "He Terminado" cuando acabes.',
        })
        
        print(f"   ✅ Pregunta de lectura creada: ID {reading_question.id}")
        print(f"      Palabras en texto: {reading_question.wpm_word_count}")
        
        # Crear pregunta WPM de escritura
        typing_question = SurveyQuestion.create({
            'survey_id': test_survey.id,
            'title': 'TEST WPM - Velocidad de Escritura',
            'question_type': 'wpm_typing',
            'wpm_mode': 'auto',
            'wpm_show_timer': True,
            'wpm_allow_paste': False,
            'wpm_instructions': 'Escribe un texto corto sobre cualquier tema.',
        })
        
        print(f"   ✅ Pregunta de escritura creada: ID {typing_question.id}")
        
        success.append("Preguntas de prueba creadas correctamente")
        
        # Generar link de prueba
        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
        test_url = f"{base_url}/survey/start/{test_survey.access_token}"
        print(f"\n   🔗 Link de prueba:")
        print(f"      {test_url}")
        
    except Exception as e:
        errors.append(f"Error al crear pregunta de prueba: {str(e)}")
        print(f"   ❌ Error: {str(e)}")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("\n" + "="*80)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*80 + "\n")
    
    if success:
        print(f"✅ ÉXITOS ({len(success)}):")
        for item in success:
            print(f"   • {item}")
        print()
    
    if warnings:
        print(f"⚠️  ADVERTENCIAS ({len(warnings)}):")
        for item in warnings:
            print(f"   • {item}")
        print()
    
    if errors:
        print(f"❌ ERRORES ({len(errors)}):")
        for item in errors:
            print(f"   • {item}")
        print()
        print("🔧 ACCIÓN REQUERIDA: Corrige los errores antes de usar el módulo.\n")
    else:
        print("🎉 ¡INSTALACIÓN EXITOSA!")
        print("   El módulo WPM está correctamente instalado y listo para usar.\n")
        print("📚 Consulta README_WPM.md para instrucciones de uso.\n")
    
    return {
        'success': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'successes': success,
    }


# Si se ejecuta como script independiente
if __name__ == '__main__':
    print("Este script debe ejecutarse desde la consola de Odoo.")
    print("\nEjemplo:")
    print(">>> exec(open('c:/ModulosOdoo18/survey_extension/verify_wpm_installation.py').read())")
    print(">>> verify_wpm_installation(env)")
