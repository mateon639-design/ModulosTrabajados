# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartnerSupplierLine(models.Model):

    _name = 'res.partner.supplier.line'
    _description = 'Vinculación Proveedor - Requisitos'

    link_up_id = fields.Many2one('res.partner.supplier', string='Vinculación')
    requirement_id = fields.Many2one('res.partner.supplier.req', string='Requisito')
    attach = fields.Binary(string='Adjunto')
    attach_name = fields.Char(string='Nombre Adjunto', default='Descargar')
    note = fields.Text(string='Observación')
    req_optional = fields.Boolean(string='Opcional')
    completed = fields.Boolean(string='Completado')