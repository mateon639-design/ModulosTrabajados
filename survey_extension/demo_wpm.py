# -*- coding: utf-8 -*-
"""
Script de Demostración WPM

Crea una encuesta de ejemplo con preguntas WPM para probar la funcionalidad.

Uso desde consola de Odoo:
    >>> exec(open('c:/ModulosOdoo18/survey_extension/demo_wpm.py').read())
    >>> create_wpm_demo(env)
"""

def create_wpm_demo(env):
    """
    Crea una encuesta de demostración con diferentes tipos de preguntas WPM
    
    Args:
        env: Entorno de Odoo
    """
    print("\n" + "="*80)
    print("CREANDO ENCUESTA DE DEMOSTRACIÓN - MÓDULO WPM")
    print("="*80 + "\n")
    
    Survey = env['survey.survey']
    Question = env['survey.question']
    
    # Eliminar encuesta demo anterior si existe
    old_survey = Survey.search([('title', '=', '📚 Demo: Evaluación de Velocidad de Lectura y Escritura')], limit=1)
    if old_survey:
        print(f"⚠️  Eliminando encuesta demo anterior (ID: {old_survey.id})...")
        old_survey.unlink()
    
    # Crear encuesta
    print("1️⃣  Creando encuesta...")
    survey = Survey.create({
        'title': '📚 Demo: Evaluación de Velocidad de Lectura y Escritura',
        'description': '''
            <p><strong>Bienvenido a la Evaluación de Velocidad de Lectura y Escritura</strong></p>
            <p>Esta encuesta mide tu capacidad de lectura y escritura en Palabras Por Minuto (WPM).</p>
            <p>Incluye:</p>
            <ul>
                <li>✅ Prueba de velocidad de lectura</li>
                <li>✅ Prueba de velocidad de escritura</li>
                <li>✅ Clasificación automática de resultados</li>
            </ul>
            <p><em>Tiempo estimado: 5-10 minutos</em></p>
        ''',
        'access_mode': 'public',
        'users_can_go_back': True,
        'is_gradable': False,
    })
    print(f"   ✅ Encuesta creada: ID {survey.id}")
    
    # ========================================================================
    # Página 1: Instrucciones
    # ========================================================================
    print("\n2️⃣  Creando preguntas...")
    
    Question.create({
        'survey_id': survey.id,
        'title': 'Instrucciones Generales',
        'question_type': 'text_box',
        'is_page': True,
        'description': '''
            <div class="alert alert-info">
                <h4>📋 Instrucciones</h4>
                <p>Esta evaluación consta de varias pruebas para medir tu velocidad de lectura y escritura.</p>
                <p><strong>Consejos:</strong></p>
                <ul>
                    <li>🎯 Lee con atención pero sin detenerte demasiado</li>
                    <li>⏱️ El temporizador comenzará automáticamente</li>
                    <li>✍️ En las pruebas de escritura, escribe de forma natural</li>
                    <li>🚫 No uses copiar/pegar en las pruebas de escritura</li>
                </ul>
                <p><em>¡Buena suerte!</em></p>
            </div>
        ''',
        'sequence': 1,
    })
    
    # ========================================================================
    # Página 2: Lectura - Texto Corto
    # ========================================================================
    
    Question.create({
        'survey_id': survey.id,
        'title': 'Parte 1: Velocidad de Lectura',
        'question_type': 'text_box',
        'is_page': True,
        'description': '<p><strong>A continuación, leerás un texto y mediremos tu velocidad de lectura.</strong></p>',
        'sequence': 10,
    })
    
    Question.create({
        'survey_id': survey.id,
        'title': '📖 Lectura - Texto Informativo (Nivel Básico)',
        'question_type': 'wpm_reading',
        'sequence': 11,
        'wpm_mode': 'reading',
        'wpm_reading_text': '''La lectura es una habilidad fundamental en el mundo moderno. No solo nos permite acceder a información, sino que también estimula nuestra imaginación y expande nuestro conocimiento. Leer regularmente mejora la concentración, aumenta el vocabulario y desarrolla el pensamiento crítico. Los buenos lectores pueden procesar información más rápidamente y retener mejor lo que leen. La velocidad de lectura varía entre personas, pero con práctica todos podemos mejorar. Lo importante no es solo leer rápido, sino también comprender y disfrutar el contenido.''',
        'wpm_show_timer': True,
        'wpm_instructions': '📚 Lee el siguiente texto con atención. Cuando termines, presiona el botón "He Terminado de Leer".',
        'wpm_min_time': 10,
        'wpm_max_time': 180,
        'wpm_slow_threshold': 150,
        'wpm_average_threshold': 250,
        'wpm_fast_threshold': 350,
    })
    
    # ========================================================================
    # Lectura - Texto Medio
    # ========================================================================
    
    Question.create({
        'survey_id': survey.id,
        'title': '📖 Lectura - Texto Técnico (Nivel Intermedio)',
        'question_type': 'wpm_reading',
        'sequence': 12,
        'wpm_mode': 'reading',
        'wpm_reading_text': '''Los sistemas operativos modernos utilizan múltiples capas de abstracción para gestionar los recursos del hardware. El kernel actúa como intermediario entre las aplicaciones y el hardware físico, proporcionando servicios esenciales como la gestión de memoria, el control de procesos y el manejo de dispositivos de entrada y salida. La planificación de procesos determina qué tareas se ejecutan y en qué orden, optimizando el uso del procesador. Los sistemas de archivos organizan y almacenan datos de manera eficiente, permitiendo acceso rápido y seguro a la información. La memoria virtual extiende la capacidad física de RAM mediante el uso del disco duro, permitiendo ejecutar más aplicaciones simultáneamente. Los controladores de dispositivos traducen las instrucciones genéricas del sistema operativo en comandos específicos que el hardware puede entender y ejecutar correctamente.''',
        'wpm_show_timer': True,
        'wpm_instructions': '💻 Este es un texto técnico. Lee normalmente sin preocuparte por palabras que no conozcas.',
        'wpm_min_time': 15,
        'wpm_max_time': 300,
        'wpm_slow_threshold': 180,
        'wpm_average_threshold': 280,
        'wpm_fast_threshold': 380,
    })
    
    # ========================================================================
    # Página 3: Escritura
    # ========================================================================
    
    Question.create({
        'survey_id': survey.id,
        'title': 'Parte 2: Velocidad de Escritura',
        'question_type': 'text_box',
        'is_page': True,
        'description': '<p><strong>Ahora mediremos tu velocidad de escritura.</strong></p>',
        'sequence': 20,
    })
    
    Question.create({
        'survey_id': survey.id,
        'title': '⌨️ Escritura Libre (2 minutos)',
        'question_type': 'wpm_typing',
        'sequence': 21,
        'wpm_mode': 'auto',
        'wpm_show_timer': True,
        'wpm_allow_paste': False,
        'wpm_instructions': '''
            ✍️ Escribe sobre cualquiera de estos temas durante aproximadamente 2 minutos:
            
            • Tu día típico
            • Un libro o película favorita
            • Tus pasatiempos o intereses
            • Un lugar que te gustaría visitar
            
            💡 Consejo: Escribe de forma natural, sin preocuparte demasiado por errores.
            El temporizador comenzará cuando escribas la primera palabra.
        ''',
        'wpm_min_time': 30,
        'wpm_max_time': 180,
        'wpm_slow_threshold': 30,
        'wpm_average_threshold': 60,
        'wpm_fast_threshold': 80,
    })
    
    Question.create({
        'survey_id': survey.id,
        'title': '⌨️ Transcripción (Escribir lo que lees)',
        'question_type': 'wpm_typing',
        'sequence': 22,
        'wpm_mode': 'auto',
        'wpm_show_timer': True,
        'wpm_allow_paste': False,
        'wpm_instructions': '''
            📝 Transcribe el siguiente texto exactamente como aparece:
            
            "La práctica constante es la clave para mejorar cualquier habilidad. 
            La velocidad de escritura no es la excepción. Con dedicación y ejercicio 
            regular, es posible duplicar o triplicar la velocidad inicial en pocos meses."
            
            ⏱️ Tiempo recomendado: 1-2 minutos
        ''',
        'wpm_min_time': 20,
        'wpm_max_time': 180,
        'wpm_slow_threshold': 35,
        'wpm_average_threshold': 65,
        'wpm_fast_threshold': 90,
    })
    
    # ========================================================================
    # Página Final
    # ========================================================================
    
    Question.create({
        'survey_id': survey.id,
        'title': '¡Gracias por Participar!',
        'question_type': 'text_box',
        'is_page': True,
        'description': '''
            <div class="alert alert-success">
                <h4>✅ Evaluación Completada</h4>
                <p>Has completado la evaluación de velocidad de lectura y escritura.</p>
                <p><strong>Tus resultados han sido guardados y procesados automáticamente.</strong></p>
                
                <hr/>
                
                <h5>📊 Referencias de Velocidad:</h5>
                
                <p><strong>Lectura:</strong></p>
                <ul>
                    <li>🐢 Básico: &lt; 150 WPM</li>
                    <li>📖 Promedio: 150-250 WPM</li>
                    <li>🚀 Avanzado: 250-350 WPM</li>
                    <li>⚡ Experto: &gt; 350 WPM</li>
                </ul>
                
                <p><strong>Escritura:</strong></p>
                <ul>
                    <li>🐢 Principiante: &lt; 30 WPM</li>
                    <li>⌨️ Básico: 30-60 WPM</li>
                    <li>💪 Intermedio: 60-80 WPM</li>
                    <li>🏆 Avanzado: &gt; 80 WPM</li>
                </ul>
                
                <p><em>¡Gracias por tu tiempo!</em></p>
            </div>
        ''',
        'sequence': 30,
    })
    
    print(f"   ✅ Creadas {len(survey.question_ids)} preguntas")
    
    # ========================================================================
    # Generar link de acceso
    # ========================================================================
    print("\n3️⃣  Generando link de acceso...")
    
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
    public_url = f"{base_url}/survey/start/{survey.access_token}"
    
    print(f"\n{'='*80}")
    print("✅ ENCUESTA DEMO CREADA EXITOSAMENTE")
    print(f"{'='*80}\n")
    
    print(f"📋 Información de la encuesta:")
    print(f"   ID: {survey.id}")
    print(f"   Título: {survey.title}")
    print(f"   Preguntas: {len(survey.question_ids)}")
    print(f"   Token: {survey.access_token}")
    
    print(f"\n🔗 Link público:")
    print(f"   {public_url}")
    
    print(f"\n📊 Tipos de pregunta incluidos:")
    for q in survey.question_ids.filtered(lambda x: not x.is_page):
        print(f"   • {q.title[:60]}...")
        print(f"     Tipo: {dict(q._fields['question_type'].selection).get(q.question_type)}")
        if q.question_type in ('wpm_reading', 'wpm_typing'):
            if q.question_type == 'wpm_reading':
                print(f"     Palabras: {q.wpm_word_count}")
            print(f"     Umbrales: {q.wpm_slow_threshold} / {q.wpm_average_threshold} / {q.wpm_fast_threshold} WPM")
    
    print(f"\n{'='*80}\n")
    
    return survey


# Si se ejecuta como script
if __name__ == '__main__':
    print("Este script debe ejecutarse desde la consola de Odoo.")
    print("\nEjemplo:")
    print(">>> exec(open('c:/ModulosOdoo18/survey_extension/demo_wpm.py').read())")
    print(">>> survey = create_wpm_demo(env)")
