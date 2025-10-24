
from datetime import timedelta, date
from odoo import models, fields, api
import html

class MonitoreoAgent(models.Model):
    _name = 'monitoreo.agent'
    _description = 'Agente Monitoreado'

    # --- Datos básicos del agente ---
    name = fields.Char("Nombre", required=True)
    state = fields.Selection([
        ('online', 'En línea'),
        ('offline', 'Desconectado'),
        ('error', 'Error'),
    ], string="Estado", default="offline")
    last_update = fields.Datetime("Última Actualización", default=fields.Datetime.now)

    # --- Relación con llamadas ---
    call_ids = fields.One2many('monitoreo.call', 'agent_id', string='Llamadas')
    call_ids_7d = fields.One2many(
        'monitoreo.call',
        string='Llamadas (7 días)',
        compute='_compute_call_ids_7d',
        readonly=True,
    )

    # --- Estadísticas de llamadas ---
    call_count_today = fields.Integer("Llamadas Hoy", compute="_compute_call_count_today")
    calls_total_7d = fields.Integer("Total Llamadas 7 días", compute="_compute_calls_per_day")

    # --- Llamadas por día (últimos 7 días) ---
    calls_day_1 = fields.Integer("Llamadas Día 1", compute="_compute_calls_per_day")  # Hoy
    calls_day_2 = fields.Integer("Llamadas Día 2", compute="_compute_calls_per_day")  # Ayer
    calls_day_3 = fields.Integer("Llamadas Día 3", compute="_compute_calls_per_day")
    calls_day_4 = fields.Integer("Llamadas Día 4", compute="_compute_calls_per_day")
    calls_day_5 = fields.Integer("Llamadas Día 5", compute="_compute_calls_per_day")
    calls_day_6 = fields.Integer("Llamadas Día 6", compute="_compute_calls_per_day")
    calls_day_7 = fields.Integer("Llamadas Día 7", compute="_compute_calls_per_day")

    # --- Porcentajes para gráfico de barras (visualización) ---
    calls_day_1_percent = fields.Integer("Porcentaje Día 1", compute="_compute_calls_per_day")
    calls_day_2_percent = fields.Integer("Porcentaje Día 2", compute="_compute_calls_per_day")
    calls_day_3_percent = fields.Integer("Porcentaje Día 3", compute="_compute_calls_per_day")
    calls_day_4_percent = fields.Integer("Porcentaje Día 4", compute="_compute_calls_per_day")
    calls_day_5_percent = fields.Integer("Porcentaje Día 5", compute="_compute_calls_per_day")
    calls_day_6_percent = fields.Integer("Porcentaje Día 6", compute="_compute_calls_per_day")
    calls_day_7_percent = fields.Integer("Porcentaje Día 7", compute="_compute_calls_per_day")

    # --- Métodos computados ---
    @api.depends('call_ids.start_datetime')
    def _compute_call_count_today(self):
        today = fields.Date.today()
        tomorrow = today + timedelta(days=1)
        for rec in self:
            rec.call_count_today = self.env['monitoreo.call'].search_count([
                ('agent_id', '=', rec.id),
                ('start_datetime', '>=', today),
                ('start_datetime', '<', tomorrow),
            ])

    @api.depends('call_ids.start_datetime')
    def _compute_calls_per_day(self):
        for rec in self:
            today = date.today()
            # Inicializar todos los contadores en 0
            rec.calls_day_1 = 0
            rec.calls_day_2 = 0
            rec.calls_day_3 = 0
            rec.calls_day_4 = 0
            rec.calls_day_5 = 0
            rec.calls_day_6 = 0
            rec.calls_day_7 = 0
            rec.calls_total_7d = 0

            if rec.id:
                total_calls = 0
                call_counts = []
                # Calcular para cada día (últimos 7 días)
                for i in range(7):
                    day_date = today - timedelta(days=i)
                    next_day = day_date + timedelta(days=1)
                    call_count = self.env['monitoreo.call'].search_count([
                        ('agent_id', '=', rec.id),
                        ('start_datetime', '>=', day_date),
                        ('start_datetime', '<', next_day),
                    ])
                    setattr(rec, f'calls_day_{i+1}', call_count)
                    call_counts.append(call_count)
                    total_calls += call_count
                rec.calls_total_7d = total_calls
                # Calcular porcentajes para barras horizontales
                max_calls = max(call_counts) if call_counts and max(call_counts) > 0 else 1
                for i, count in enumerate(call_counts):
                    percent = int((count / max_calls) * 100) if max_calls > 0 else 0
                    setattr(rec, f'calls_day_{i+1}_percent', percent)

    @api.depends('call_ids.start_datetime')
    def _compute_call_ids_7d(self):
        limit_from = fields.Datetime.now() - timedelta(days=7)
        Call = self.env['monitoreo.call']
        for rec in self:
            if rec.id:
                rec.call_ids_7d = Call.search([
                    ('agent_id', '=', rec.id),
                    ('start_datetime', '>=', limit_from),
                ], order='start_datetime desc')
            else:
                rec.call_ids_7d = Call.browse()

    # --- Acción para abrir gráfico de llamadas ---
    def action_view_calls_graph_7d(self):
        """Abrir gráfico de llamadas de los últimos 7 días para este agente"""
        limit_from = fields.Datetime.now() - timedelta(days=7)
        return {
            'type': 'ir.actions.act_window',
            'name': f'Gráfico de Llamadas - {self.name} (7 días)',
            'res_model': 'monitoreo.call',
            'view_mode': 'graph',
            'view_id': self.env.ref('monitoreo_agente.view_monitoreo_call_graph').id,
            'domain': [
                ('agent_id', '=', self.id),
                ('start_datetime', '>=', limit_from),
            ],
            'target': 'new',
            'context': {
                'graph_measure': 'duration',
                'graph_mode': 'line',
                'graph_groupbys': ['start_datetime:day'],
            }
        }

    # --- Servicio de alertas vinculadas a retain.call.history ---
    @api.model
    def send_permission_denied_alert(self, call_vals=None, email_to='edcamilo2016@gmail.com', custom_message=None):
        """
        Envía una alerta por correo cuando se detecta el error de "Permiso denegado por el proveedor de telefonía".
        Puede ser llamado desde retain_call_history al crear/actualizar la llamada.

        :param call_vals: dict o record con datos de la llamada (acepta record de retain.call.history)
        :param email_to: destinatario
        :param custom_message: mensaje personalizado opcional
        """
        if not call_vals:
            return False

        # Normalizar a dict de valores para construir el email
        if hasattr(call_vals, 'id'):
            data = {
                'call_id': call_vals.call_id,
                'agent_name': call_vals.agent_name,
                'from_number': call_vals.from_number,
                'to_number': call_vals.to_number,
                'call_date': call_vals.call_date,
                'disconnection_reason': call_vals.disconnection_reason,
                'sequence': call_vals.sequence,
            }
        else:
            data = call_vals

        subject = 'Alerta: Permiso denegado por el proveedor de telefonía'
        if custom_message:
            body_text = custom_message
        else:
            body_text = (
                f"¡Atención! Se detectó una llamada con el siguiente error:\n\n"
                f"Permiso denegado por el proveedor de telefonía.\n\n"
                f"Detalles de la llamada:\n"
                f"Secuencia: {data.get('sequence') or 'N/A'}\n"
                f"ID de llamada: {data.get('call_id') or 'N/A'}\n"
                f"Agente: {data.get('agent_name') or 'N/A'}\n"
                f"Número origen: {data.get('from_number') or 'N/A'}\n"
                f"Número destino: {data.get('to_number') or 'N/A'}\n"
                f"Fecha y hora: {data.get('call_date') or 'N/A'}\n"
                f"Motivo: {data.get('disconnection_reason') or ''}\n"
            )

        body_html = f"<pre>{html.escape(body_text)}</pre>"
        # Crear registro de alerta para visibilidad en el dashboard
        agent_id = False
        if data.get('agent_name'):
            agent = self.env['monitoreo.agent'].search([('name', 'ilike', data.get('agent_name'))], limit=1)
            agent_id = agent.id or False
        self.env['monitoreo.alert'].create({
            'name': 'Permiso denegado por el proveedor de telefonía',
            'alert_type': 'call_failed',
            'severity': 'critical',
            'state': 'pending',
            'description': body_text,
            'agent_id': agent_id,
        })

        self.env['mail.mail'].create({
            'subject': subject,
            'body_html': body_html,
            'email_to': email_to,
            'auto_delete': True,
        }).send()
        return True
