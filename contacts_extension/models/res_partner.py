# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """
    Extensión del modelo res.partner (Contactos)
    
    Este modelo hereda de res.partner y permite agregar campos personalizados,
    métodos adicionales y lógica de negocio específica para contactos.
    """
    
    _inherit = 'res.partner'
    _description = 'Extensión de Contactos'
    
    # ===========================
    # CAMPOS PERSONALIZADOS
    # ===========================
    
    # Ejemplo de campo personalizado (puedes agregar más según necesites)
    custom_reference = fields.Char(
        string='Referencia Personalizada',
        help='Campo de ejemplo para referencia interna del contacto',
        copy=False,
        index=True,
    )
    
    custom_notes = fields.Text(
        string='Notas Personalizadas',
        help='Notas adicionales sobre el contacto',
    )
    
    custom_active_date = fields.Date(
        string='Fecha de Activación',
        help='Fecha en que el contacto fue activado',
        default=fields.Date.context_today,
    )
    
    custom_priority = fields.Selection(
        [
            ('low', 'Baja'),
            ('medium', 'Media'),
            ('high', 'Alta'),
            ('urgent', 'Urgente'),
        ],
        string='Prioridad',
        default='medium',
        help='Nivel de prioridad del contacto',
    )
    
    custom_is_verified = fields.Boolean(
        string='Verificado',
        default=False,
        help='Indica si el contacto ha sido verificado',
    )
    
    # ===========================
    # CAMPOS DE TRAZABILIDAD DE IMPORTACIÓN
    # ===========================
    
    import_source = fields.Char(
        string='Origen de Importación',
        help='Nombre del archivo desde el cual fue importado este contacto',
        readonly=True,
        copy=False,
    )
    
    import_date = fields.Datetime(
        string='Fecha de Importación',
        help='Fecha y hora en que se importó o actualizó este contacto',
        readonly=True,
        copy=False,
    )
    
    import_region = fields.Char(
        string='Región de Importación',
        help='Región especificada durante la importación',
        readonly=True,
        copy=False,
    )
    
    import_type = fields.Selection([
        ('student', 'Estudiante'),
        ('teacher', 'Profesor'),
    ], string='Tipo de Importación', 
       help='Tipo de contacto especificado en la importación',
       readonly=True,
       copy=False,
    )
    
    last_import_update = fields.Datetime(
        string='Última Actualización por Importación',
        help='Fecha de la última vez que este contacto fue actualizado por una importación',
        readonly=True,
        copy=False,
    )
    
    import_count = fields.Integer(
        string='Número de Importaciones',
        default=0,
        help='Cantidad de veces que este contacto ha sido importado/actualizado',
        readonly=True,
        copy=False,
    )
    
    # ===========================
    # HISTORIAL DE ENCUESTAS
    # ===========================
    
    survey_count = fields.Integer(
        string='Total de Encuestas',
        compute='_compute_survey_statistics',
        help='Cantidad total de encuestas en las que ha participado',
    )
    
    survey_completed_count = fields.Integer(
        string='Encuestas Completadas',
        compute='_compute_survey_statistics',
        help='Cantidad de encuestas completadas (finalizadas)',
    )
    
    survey_in_progress_count = fields.Integer(
        string='Encuestas en Proceso',
        compute='_compute_survey_statistics',
        help='Cantidad de encuestas iniciadas pero no finalizadas',
    )
    
    last_survey_date = fields.Datetime(
        string='Última Encuesta',
        compute='_compute_survey_statistics',
        help='Fecha de la última encuesta respondida',
    )
    
    survey_average_score = fields.Float(
        string='Promedio de Puntaje',
        compute='_compute_survey_statistics',
        digits=(16, 2),
        help='Promedio de puntajes obtenidos en encuestas calificables',
    )
    
    # ===========================
    # MÉTODOS COMPUTADOS
    # ===========================
    
    def _compute_survey_statistics(self):
        """
        Calcula estadísticas de participación en encuestas.
        Solo funciona si el módulo 'survey' está instalado.
        """
        # Verificar si el módulo survey está instalado
        if 'survey.user_input' not in self.env:
            # Si no está instalado, poner valores por defecto
            for partner in self:
                partner.survey_count = 0
                partner.survey_completed_count = 0
                partner.survey_in_progress_count = 0
                partner.last_survey_date = False
                partner.survey_average_score = 0.0
            return
        
        for partner in self:
            try:
                # Buscar las encuestas del partner
                inputs = self.env['survey.user_input'].search([
                    ('partner_id', '=', partner.id)
                ])
                
                # Total de encuestas
                partner.survey_count = len(inputs)
                
                # Encuestas completadas
                completed = inputs.filtered(lambda i: i.state == 'done')
                partner.survey_completed_count = len(completed)
                
                # Encuestas en proceso
                in_progress = inputs.filtered(lambda i: i.state == 'in_progress')
                partner.survey_in_progress_count = len(in_progress)
                
                # Última fecha de encuesta (usar create_date o end_datetime)
                if completed:
                    # Intentar obtener end_datetime si existe, sino create_date
                    last_dates = []
                    for inp in completed:
                        if hasattr(inp, 'end_datetime') and inp.end_datetime:
                            last_dates.append(inp.end_datetime)
                        elif inp.create_date:
                            last_dates.append(inp.create_date)
                    
                    if last_dates:
                        partner.last_survey_date = max(last_dates)
                    else:
                        partner.last_survey_date = False
                else:
                    partner.last_survey_date = False
                
                # Promedio de puntajes (solo encuestas calificadas)
                scored_inputs = completed.filtered(lambda i: hasattr(i, 'x_score_percent') and i.x_score_percent > 0)
                if scored_inputs:
                    partner.survey_average_score = sum(scored_inputs.mapped('x_score_percent')) / len(scored_inputs)
                else:
                    partner.survey_average_score = 0.0
            except Exception:
                # En caso de error, valores por defecto
                partner.survey_count = 0
                partner.survey_completed_count = 0
                partner.survey_in_progress_count = 0
                partner.last_survey_date = False
                partner.survey_average_score = 0.0
    
    @api.depends('name', 'custom_reference')
    def _compute_display_name(self):
        """
        Sobrescribe el display_name para incluir la referencia personalizada
        si está disponible.
        """
        for partner in self:
            name = partner.name or ''
            if partner.custom_reference:
                name = f"[{partner.custom_reference}] {name}"
            partner.display_name = name
    
    # ===========================
    # CONSTRAINS Y VALIDACIONES
    # ===========================
    
    @api.constrains('custom_reference')
    def _check_custom_reference(self):
        """
        Valida que la referencia personalizada sea única si está definida.
        """
        for partner in self:
            # Solo validar si hay un valor en custom_reference
            if partner.custom_reference and partner.custom_reference.strip():
                duplicate = self.search([
                    ('id', '!=', partner.id),
                    ('custom_reference', '=', partner.custom_reference),
                ], limit=1)
                if duplicate:
                    raise ValidationError(
                        _('La referencia personalizada "%s" ya existe para el contacto "%s".') 
                        % (partner.custom_reference, duplicate.name)
                    )
    
    # ===========================
    # MÉTODOS ONCHANGE
    # ===========================
    
    @api.onchange('custom_priority')
    def _onchange_custom_priority(self):
        """
        Ejemplo de método onchange que muestra un mensaje cuando
        se selecciona prioridad urgente.
        """
        if self.custom_priority == 'urgent':
            return {
                'warning': {
                    'title': _('Prioridad Urgente'),
                    'message': _('Has marcado este contacto como urgente. '
                                'Asegúrate de darle seguimiento inmediato.'),
                }
            }
    
    # ===========================
    # MÉTODOS CRUD PERSONALIZADOS
    # ===========================
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para agregar lógica personalizada
        al crear nuevos contactos.
        """
        # Puedes agregar lógica adicional aquí antes de crear
        partners = super(ResPartner, self).create(vals_list)
        
        # Puedes agregar lógica adicional aquí después de crear
        for partner in partners:
            if partner.custom_is_verified:
                # Ejemplo: registrar en log cuando se crea un contacto verificado
                partner.message_post(
                    body=_('Contacto creado y verificado el %s') % fields.Date.today()
                )
        
        return partners
    
    def write(self, vals):
        """
        Sobrescribe el método write para agregar lógica personalizada
        al actualizar contactos.
        """
        # Detectar si se está verificando el contacto
        if vals.get('custom_is_verified') and not self.custom_is_verified:
            vals['custom_active_date'] = fields.Date.today()
        
        result = super(ResPartner, self).write(vals)
        
        # Lógica adicional después de actualizar
        if vals.get('custom_is_verified'):
            for partner in self:
                partner.message_post(
                    body=_('Contacto verificado el %s') % fields.Date.today()
                )
        
        return result
    
    # ===========================
    # MÉTODOS DE NEGOCIO
    # ===========================
    
    def action_verify_contact(self):
        """
        Acción para verificar el contacto manualmente.
        """
        self.ensure_one()
        self.write({
            'custom_is_verified': True,
            'custom_active_date': fields.Date.today(),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Contacto Verificado'),
                'message': _('El contacto "%s" ha sido verificado exitosamente.') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_unverify_contact(self):
        """
        Acción para remover la verificación del contacto.
        """
        self.ensure_one()
        self.custom_is_verified = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Verificación Removida'),
                'message': _('La verificación del contacto "%s" ha sido removida.') % self.name,
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_view_surveys(self):
        """
        Acción para ver todas las encuestas del contacto.
        """
        self.ensure_one()
        return {
            'name': _('Encuestas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_partner_id': self.id,
            },
            'target': 'current',
        }
    
    def action_view_completed_surveys(self):
        """
        Acción para ver solo las encuestas completadas del contacto.
        """
        self.ensure_one()
        return {
            'name': _('Encuestas Completadas - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'view_mode': 'list,form',
            'domain': [
                ('partner_id', '=', self.id),
                ('state', '=', 'done'),
            ],
            'context': {
                'default_partner_id': self.id,
            },
            'target': 'current',
        }
    
    # ===========================
    # MÉTODOS DE BÚSQUEDA
    # ===========================
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, order=None):
        """
        Extiende la búsqueda por nombre para incluir la referencia personalizada.
        """
        args = args or []
        if name:
            args = [
                '|',
                ('custom_reference', operator, name),
                ('name', operator, name),
            ] + args
        return super(ResPartner, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, order=order
        )
