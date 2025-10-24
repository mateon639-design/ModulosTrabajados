# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta, date, time

class ResPartnerSupplier(models.Model):

    _name = 'res.partner.supplier'
    _description = 'Vinculación Proveedor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Codigo', required=True, copy=False, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Proveedor', required=True, tracking=True)
    state = fields.Selection(string='Estado', selection=[
        ('pre_registered', 'Pre-Inscrito'), ('pre_validate', 'En Validación'), ('requires_specifications', 'Requiere Especificaciones'), 
        ('done', 'Aprobado'), ('refused', 'Rechazado'), ('under_renovation', 'En Renovación')], default='pre_registered', tracking=True)
    date_approval = fields.Date(string='Fecha aprobación')
    approbal_uid = fields.Many2one('res.users', string='Usuario aprobador')
    active = fields.Boolean(string='Activa', default=True)
    line_ids = fields.One2many('res.partner.supplier.line', 'link_up_id', string='Requisitos')
    progress_status = fields.Float(string='Progreso de registro', compute='_get_progress')
    note = fields.Text(string='Observaciones')
    

    info_proveedor = fields.Boolean(string='Proveedor')
    info_tributaria = fields.Boolean(string='Tributaria')
    info_metodo_pago = fields.Boolean(string='Metodo Pago')
    info_referencias = fields.Boolean(string='Referencias')
    info_requisitos = fields.Boolean(string='Requisitos')
    info_politicas = fields.Boolean(string='Politicas')

    contract_ids = fields.One2many('res.partner.supplier.contract', inverse_name='link_up_id', string='Contratos / Convenios')
    

    def send_approval_email(self):
        for supplier in self: 
            email = self.env.ref("ox_supplier_portal.supplier_register_status_approval_template").send_mail(supplier.id, force_send=True, raise_exception=False)
            email_sent = self.env['mail.mail'].search([('id','=',email)])
            supplier.partner_id.message_post(body=email_sent.body)

    def action_done(self, send_message=True):
        self.date_approval = datetime.today()
        self.approbal_uid = self.env.uid
        self.state = 'done'
        self.env.cr.commit()
        if send_message:
            self.send_approval_email()
        

    def action_refuse(self):
        self.state = 'refused'

    def action_restart(self):
        self.state = 'pre_registered'

    def action_requires_specifications(self):
        if not self.note:
            raise ValidationError('Debe ingresar la observación indicando al proveedor cuales son los requerimientos a especificar en el proceso de registro!')
        self.state = 'requires_specifications'

    def _get_progress_portal(self):
        for supplier in self:
            return "width:" + str(int(supplier.progress_status)) + "%;"

    def _get_progress(self):
        for supplier in self:
            progress_status = 5
            progress_status += 0 if not supplier.info_proveedor else 10
            progress_status += 0 if not supplier.info_tributaria else 15
            progress_status += 0 if not supplier.info_metodo_pago else 20
            progress_status += 0 if not supplier.info_referencias else 20
            progress_status += 0 if not supplier.info_requisitos else 20
            progress_status += 0 if not supplier.info_politicas else 10
            supplier.progress_status = progress_status
        
        return progress_status
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('res.partner.supplier.seq', None) or _('New')
        result = super(ResPartnerSupplier, self).create(vals)
        return result


    _sql_constraints = [
        ('partner_id_uniq', 'UNIQUE (partner_id)',  'El proveedor ya cuenta con una vinculación asignada!')
    ]