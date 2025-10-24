#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar estadísticas de encuestas.
Ejecutar desde el shell de Odoo.

Uso:
    python "C:\Program Files\Odoo 18.0.20251001\server\odoo-bin" shell -d mateo
    exec(open(r'C:\ModulosOdoo18\survey_extension\diagnose_stats.py').read())
"""

import logging

_logger = logging.getLogger(__name__)

def diagnose_survey_stats():
    """Diagnostica por qué las estadísticas pueden estar vacías."""
    
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO DE ESTADÍSTICAS DE ENCUESTAS")
    print("=" * 80)
    
    try:
        # 1. Verificar encuestas
        surveys = env['survey.survey'].search([])
        print(f"\n📋 Total de encuestas: {len(surveys)}")
        
        for survey in surveys:
            print(f"\n{'─' * 80}")
            print(f"📊 Encuesta: {survey.title}")
            print(f"   ID: {survey.id}")
            
            # 2. Verificar preguntas
            questions = env['survey.question'].search([
                ('survey_id', '=', survey.id)
            ])
            print(f"   ❓ Total preguntas: {len(questions)}")
            
            # 3. Verificar preguntas de selección
            choice_questions = questions.filtered(
                lambda q: q.question_type in ('simple_choice', 'multiple_choice')
            )
            print(f"   ✓ Preguntas de selección: {len(choice_questions)}")
            
            if choice_questions:
                for q in choice_questions:
                    answers = env['survey.question.answer'].search([
                        ('question_id', '=', q.id)
                    ])
                    print(f"      • {q.title[:50]}... ({q.question_type})")
                    print(f"        Opciones: {len(answers)}")
            
            # 4. Verificar participaciones
            user_inputs = env['survey.user_input'].search([
                ('survey_id', '=', survey.id)
            ])
            completed = user_inputs.filtered(lambda u: u.state == 'done')
            print(f"   👥 Participaciones: {len(user_inputs)} (Completadas: {len(completed)})")
            
            # 5. Verificar líneas de respuesta
            if completed:
                lines = env['survey.user_input.line'].search([
                    ('user_input_id', 'in', completed.ids),
                    ('suggested_answer_id', '!=', False)
                ])
                print(f"   📝 Líneas de respuesta con opción seleccionada: {len(lines)}")
                
                if lines:
                    # Agrupar por pregunta
                    questions_with_answers = lines.mapped('question_id')
                    print(f"   ✅ Preguntas con respuestas: {len(questions_with_answers)}")
            
            # 6. Verificar estadísticas generadas
            stats = env['survey.question.stats'].search([
                ('survey_id', '=', survey.id)
            ])
            print(f"   📈 Registros de estadísticas: {len(stats)}")
            
            if stats:
                print(f"\n   🎯 Muestra de estadísticas:")
                for stat in stats[:5]:
                    print(f"      • {stat.question_title[:40]}: {stat.answer_text[:30]} - {stat.answer_percentage}% ({stat.answer_count} votos)")
            else:
                print(f"   ⚠️  NO HAY ESTADÍSTICAS GENERADAS")
                
                # Diagnosticar por qué
                if not choice_questions:
                    print(f"   ❌ Motivo: La encuesta no tiene preguntas de selección")
                elif not completed:
                    print(f"   ❌ Motivo: No hay participaciones completadas")
                else:
                    choice_with_answers = choice_questions.filtered(
                        lambda q: env['survey.question.answer'].search_count([
                            ('question_id', '=', q.id)
                        ]) > 0
                    )
                    if not choice_with_answers:
                        print(f"   ❌ Motivo: Las preguntas de selección no tienen opciones configuradas")
                    else:
                        print(f"   ❌ Motivo: Las participaciones completadas no tienen respuestas a preguntas de selección")
        
        print("\n" + "=" * 80)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("=" * 80)
        
        # 7. Intentar regenerar la vista
        print("\n🔄 Intentando regenerar la vista SQL...")
        try:
            env['survey.question.stats'].init()
            env.cr.commit()
            print("✅ Vista SQL regenerada correctamente")
            
            # Verificar de nuevo
            total_stats = env['survey.question.stats'].search([])
            print(f"📊 Total de registros de estadísticas después de regenerar: {len(total_stats)}")
            
        except Exception as e:
            print(f"❌ Error al regenerar vista: {e}")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()


# Ejecutar automáticamente
if __name__ == '__main__' or 'env' in dir():
    diagnose_survey_stats()
