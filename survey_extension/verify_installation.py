# -*- coding: utf-8 -*-
"""
Script de verificación post-instalación
Ejecutar en la consola de Odoo para verificar que todo esté correcto
"""

def verify_survey_extension_installation(env):
    """
    Verifica que todas las nuevas funcionalidades estén correctamente instaladas.
    
    Uso:
        En la consola de Odoo:
        >>> from odoo.addons.survey_extension.verify_installation import verify_survey_extension_installation
        >>> verify_survey_extension_installation(env)
    """
    print("=" * 80)
    print("VERIFICACIÓN DE INSTALACIÓN - Survey Extension v1.4.0")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    # 1. Verificar modelos
    print("\n1. Verificando modelos...")
    try:
        env['survey.user_input'].search([], limit=1)
        print("   ✅ survey.user_input accesible")
    except Exception as e:
        errors.append(f"   ❌ Error en survey.user_input: {e}")
    
    try:
        env['survey.question.stats'].search([], limit=1)
        print("   ✅ survey.question.stats accesible")
    except Exception as e:
        errors.append(f"   ❌ Error en survey.question.stats: {e}")
    
    try:
        env['survey.dashboard'].search([], limit=1)
        print("   ✅ survey.dashboard accesible")
    except Exception as e:
        errors.append(f"   ❌ Error en survey.dashboard: {e}")
    
    # 2. Verificar campos en survey.user_input
    print("\n2. Verificando campos en survey.user_input...")
    required_fields = [
        'x_survey_duration',
        'x_survey_duration_display',
        'x_ranking_position',
        'x_ranking_total',
        'x_ranking_percentile',
        'x_ranking_medal',
    ]
    
    model_fields = env['survey.user_input'].fields_get()
    for field in required_fields:
        if field in model_fields:
            print(f"   ✅ Campo {field} existe")
        else:
            errors.append(f"   ❌ Campo {field} NO existe")
    
    # 3. Verificar campos en survey.survey
    print("\n3. Verificando campos en survey.survey...")
    survey_fields = []
    
    survey_model_fields = env['survey.survey'].fields_get()
    for field in survey_fields:
        if field in survey_model_fields:
            print(f"   ✅ Campo {field} existe")
        else:
            errors.append(f"   ❌ Campo {field} NO existe")
    
    # 4. Verificar vistas
    print("\n4. Verificando vistas...")
    views = [
        'survey_extension.survey_user_input_form_device_info',
        'survey_extension.survey_user_input_form_ranking',
        'survey_extension.survey_user_input_kanban_ranking',
        'survey_extension.survey_question_stats_kanban',
        'survey_extension.survey_dashboard_kanban',
        'survey_extension.action_survey_ranking',
        'survey_extension.action_survey_question_stats',
        'survey_extension.action_survey_dashboard',
    ]
    
    for view_xmlid in views:
        try:
            env.ref(view_xmlid)
            print(f"   ✅ Vista {view_xmlid} existe")
        except Exception as e:
            warnings.append(f"   ⚠️  Vista {view_xmlid} no encontrada")
    
    # 5. Verificar datos de ejemplo
    print("\n5. Verificando datos...")
    user_inputs = env['survey.user_input'].search([('x_survey_duration', '>', 0)], limit=5)
    if user_inputs:
        print(f"   ✅ {len(user_inputs)} participaciones con duración calculada")
        for ui in user_inputs:
            print(f"      - {ui.id}: {ui.x_survey_duration_display}")
    else:
        warnings.append("   ⚠️  No hay participaciones con duración calculada (normal si no hay datos)")
    
    # 6. Verificar vistas SQL
    print("\n6. Verificando vistas SQL...")
    env.cr.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('survey_question_stats', 'survey_dashboard')
    """)
    sql_views = env.cr.fetchall()
    if len(sql_views) == 2:
        print("   ✅ Vistas SQL creadas correctamente")
        for view in sql_views:
            print(f"      - {view[0]}")
    else:
        errors.append(f"   ❌ Solo {len(sql_views)}/2 vistas SQL creadas")
    
    # 7. Verificar archivos JavaScript
    print("\n7. Verificando recursos JavaScript...")
    # No podemos verificar archivos directamente, pero podemos verificar que estén en assets
    if 'survey_extension/static/src/js/survey_device_capture.js' in str(env['ir.module.module'].search([('name', '=', 'survey_extension')]).latest_version):
        print("   ✅ JavaScript device_capture registrado")
    else:
        warnings.append("   ⚠️  No se puede verificar JavaScript (requiere reinicio de Odoo)")
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 80)
    
    if errors:
        print(f"\n❌ ERRORES ENCONTRADOS ({len(errors)}):")
        for error in errors:
            print(error)
    else:
        print("\n✅ No se encontraron errores críticos")
    
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
        for warning in warnings:
            print(warning)
    else:
        print("\n✅ No hay advertencias")
    
    if not errors and not warnings:
        print("\n🎉 ¡INSTALACIÓN PERFECTA! Todas las funcionalidades están listas.")
    elif not errors:
        print("\n✅ Instalación correcta con advertencias menores.")
    else:
        print("\n❌ Por favor, revisa los errores y actualiza el módulo nuevamente.")
    
    print("\n" + "=" * 80)
    
    return {
        'errors': errors,
        'warnings': warnings,
        'status': 'ok' if not errors else 'error'
    }


# Función auxiliar para verificar una encuesta específica
def check_survey_stats(env, survey_id):
    """
    Verifica las estadísticas de una encuesta específica.
    
    Uso:
        >>> from odoo.addons.survey_extension.verify_installation import check_survey_stats
        >>> check_survey_stats(env, 1)
    """
    survey = env['survey.survey'].browse(survey_id)
    if not survey.exists():
        print(f"❌ Encuesta {survey_id} no existe")
        return
    
    print(f"\n{'=' * 80}")
    print(f"ESTADÍSTICAS DE ENCUESTA: {survey.title}")
    print(f"{'=' * 80}\n")
    
    # Participaciones
    inputs = env['survey.user_input'].search([('survey_id', '=', survey_id)])
    print(f"📊 Total de participaciones: {len(inputs)}")
    print(f"   - Completadas: {len(inputs.filtered(lambda x: x.state == 'done'))}")
    print(f"   - En progreso: {len(inputs.filtered(lambda x: x.state == 'in_progress'))}")
    
    # Dispositivos
    devices = inputs.filtered(lambda x: x.x_device_id).mapped('x_device_id')
    print(f"\n📱 Dispositivos:")
    print(f"   - Únicos: {len(set(devices))}")
    print(f"   - Total registros con device: {len(devices)}")
    
    # Duración
    durations = inputs.filtered(lambda x: x.x_survey_duration > 0)
    if durations:
        avg_duration = sum(durations.mapped('x_survey_duration')) / len(durations)
        print(f"\n⏱️  Tiempo de respuesta:")
        print(f"   - Promedio: {avg_duration:.0f} segundos ({avg_duration/60:.1f} minutos)")
        print(f"   - Mínimo: {min(durations.mapped('x_survey_duration')):.0f} segundos")
        print(f"   - Máximo: {max(durations.mapped('x_survey_duration')):.0f} segundos")
    
    # Ranking
    completed = inputs.filtered(lambda x: x.state == 'done' and x.score_percentage > 0)
    if completed:
        print(f"\n🏆 Ranking (Top 5):")
        top_5 = completed.sorted(lambda x: x.score_percentage, reverse=True)[:5]
        for idx, inp in enumerate(top_5, 1):
            print(f"   {idx}. {inp.x_ranking_medal or '🎖️'} - {inp.partner_id.name or inp.email}: {inp.score_percentage:.1f}%")
    
    # Estadísticas por pregunta
    stats = env['survey.question.stats'].search([('survey_id', '=', survey_id)])
    if stats:
        print(f"\n📈 Estadísticas por pregunta:")
        questions = set(stats.mapped('question_id'))
        print(f"   - Preguntas con datos: {len(questions)}")
        print(f"   - Total de registros de estadísticas: {len(stats)}")
    
    print(f"\n{'=' * 80}\n")


if __name__ == '__main__':
    print("Este script debe ejecutarse desde la consola de Odoo")
    print("Uso:")
    print("  from odoo.addons.survey_extension.verify_installation import verify_survey_extension_installation")
    print("  verify_survey_extension_installation(env)")
