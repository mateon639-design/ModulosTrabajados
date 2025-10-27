# -*- coding: utf-8 -*-
"""Modelo para el historial de importaciones."""

from odoo import api, fields, models, _


class ImportHistory(models.Model):
    """Historial de importaciones de contactos."""
    
    _name = 'import.history'
    _description = 'Historial de Importaciones'
    _order = 'import_date desc'
    _rec_name = 'file_name'

    # Información del archivo
    file_name = fields.Char(string='Archivo', required=True)
    file_type = fields.Selection([
        ('csv', 'CSV'),
        ('xlsx', 'Excel (XLSX)'),
        ('xml', 'XML'),
    ], string='Tipo de Archivo', required=True)
    
    # Información de la importación
    import_date = fields.Datetime(string='Fecha de Importación', required=True, default=fields.Datetime.now)
    contact_type = fields.Selection([
        ('student', 'Estudiante'),
        ('teacher', 'Profesor'),
    ], string='Tipo de Contacto', required=True)
    region = fields.Char(string='Región')
    
    # Estadísticas
    total_rows = fields.Integer(string='Total de Filas', default=0)
    created_count = fields.Integer(string='Contactos Creados', default=0)
    updated_count = fields.Integer(string='Contactos Actualizados', default=0)
    error_count = fields.Integer(string='Errores', default=0)
    
    # Resultados
    created_ids = fields.Many2many(
        'res.partner', 
        'history_partner_created_rel',
        'history_id', 
        'partner_id',
        string='Contactos Creados'
    )
    updated_ids = fields.Many2many(
        'res.partner', 
        'history_partner_updated_rel',
        'history_id', 
        'partner_id',
        string='Contactos Actualizados'
    )
    error_log = fields.Text(string='Log de Errores')
    
    # Usuario que realizó la importación
    user_id = fields.Many2one('res.users', string='Importado por', default=lambda self: self.env.user, required=True)
    
    # Estado
    state = fields.Selection([
        ('success', 'Exitoso'),
        ('partial', 'Parcial (con errores)'),
        ('failed', 'Fallido'),
    ], string='Estado', compute='_compute_state', store=True)
    
    # Campos computados para estadísticas
    success_rate = fields.Float(string='Tasa de Éxito (%)', compute='_compute_success_rate', store=True)

    @api.depends('total_rows', 'created_count', 'updated_count', 'error_count')
    def _compute_state(self):
        """Calcula el estado de la importación."""
        for record in self:
            if record.error_count == 0 and (record.created_count > 0 or record.updated_count > 0):
                record.state = 'success'
            elif record.error_count > 0 and (record.created_count > 0 or record.updated_count > 0):
                record.state = 'partial'
            else:
                record.state = 'failed'

    @api.depends('total_rows', 'error_count')
    def _compute_success_rate(self):
        """Calcula la tasa de éxito de la importación."""
        for record in self:
            if record.total_rows > 0:
                successful = record.total_rows - record.error_count
                record.success_rate = (successful / record.total_rows) * 100
            else:
                record.success_rate = 0.0

    def action_view_created_contacts(self):
        """Abre la vista de contactos creados."""
        self.ensure_one()
        return {
            'name': _('Contactos Creados - %s') % self.file_name,
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.created_ids.ids)],
            'context': {'create': False},
        }

    def action_view_updated_contacts(self):
        """Abre la vista de contactos actualizados."""
        self.ensure_one()
        return {
            'name': _('Contactos Actualizados - %s') % self.file_name,
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.updated_ids.ids)],
            'context': {'create': False},
        }

    def action_view_error_log(self):
        """Muestra el log de errores en un wizard."""
        self.ensure_one()
        return {
            'name': _('Log de Errores - %s') % self.file_name,
            'type': 'ir.actions.act_window',
            'res_model': 'import.history',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
        }
